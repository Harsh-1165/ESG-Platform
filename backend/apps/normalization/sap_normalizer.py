from decimal import Decimal
from datetime import datetime

from apps.normalization.units import convert_to_co2e
from .models import NormalizedRecord


SAP_HEADER_MAP = {
    'plant': 'facility_id',
    'werk': 'facility_id',
    'plant / werk': 'facility_id',
    'plant_code': 'facility_id',
    'plant id': 'facility_id',

    'fuel description': 'material_description',
    'procurement description': 'material_description',
    'material description': 'material_description',
    'description': 'material_description',
    'product description': 'material_description',

    'quantity': 'quantity',
    'qty': 'quantity',
    'menge': 'quantity',
    'amount': 'quantity',
    'quantity_ledger': 'quantity',

    'unit': 'unit',
    'uom': 'unit',
    'meins': 'unit',
    'unit of measure': 'unit',

    'posting date': 'posting_date',
    'date': 'posting_date',
    'document date': 'posting_date',
    'budat': 'posting_date',
    'postingdate': 'posting_date',
    'document_date': 'posting_date',

    'material code': 'material_code',
    'matnr': 'material_code',
    'material': 'material_code',
    'material number': 'material_code',

    'source subtype': 'source_subtype',
    'transaction type': 'source_subtype',
    'category': 'source_subtype',
}

SCOPE_CLASSIFICATION = {
    'direct': 'scope_1',
    'combustion': 'scope_1',
    'plant fuel': 'scope_1',
    'vehicle fuel': 'scope_1',
    'mobile fuel': 'scope_1',
    'process heat': 'scope_1',
    'purchased fuel': 'scope_3',
    'procurement': 'scope_3',
    'logistics': 'scope_3',
    'transport': 'scope_3',
    'scope 3': 'scope_3',
    'upstream': 'scope_3',
    'purchased goods': 'scope_3',
}

UNIT_NORMALIZATION = {
    'l': 'liters_diesel',
    'lt': 'liters_diesel',
    'ltr': 'liters_diesel',
    'liter': 'liters_diesel',
    'litre': 'liters_diesel',
    'liters': 'liters_diesel',
    'litres': 'liters_diesel',
    'kg': 'kg_CO2e',
    'g': 'kg_CO2e',
    'm3': 'liters_diesel',
    'gal': 'gallons_diesel',
    'gallon': 'gallons_diesel',
    'gallons': 'gallons_diesel',
    'us gal': 'gallons_diesel',
    'mmbtu': 'gallons_diesel',
}

DATE_FORMATS = [
    '%Y-%m-%d',
    '%d/%m/%Y',
    '%d.%m.%Y',
    '%m/%d/%Y',
    '%Y%m%d',
    '%d-%m-%Y',
    '%Y/%m/%d',
]


def normalize_header(key):
    if not key:
        return ''
    normalized = key.strip().lower().replace('-', ' ').replace('_', ' ')
    normalized = ' '.join(part for part in normalized.split() if part)
    return normalized


def canonicalize_row(raw_content):
    canonical = {}
    for original_key, value in raw_content.items():
        key = normalize_header(original_key)
        canonical_key = SAP_HEADER_MAP.get(key, key)
        canonical[canonical_key] = value
    return canonical


def parse_decimal(value):
    if value is None:
        raise ValueError('Missing quantity')

    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))

    if isinstance(value, str):
        cleaned = value.strip().replace(' ', '')
        if cleaned.count(',') and not cleaned.count('.'):
            cleaned = cleaned.replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
        return Decimal(cleaned)

    raise ValueError(f'Unsupported quantity format: {value}')


def parse_sap_date(value):
    if value is None or str(value).strip() == '':
        raise ValueError('Missing posting date')

    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        cleaned = value.strip()
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(cleaned, fmt).date()
            except ValueError:
                continue
    raise ValueError(f'Unsupported posting date format: {value}')


def normalize_sap_unit(unit_value, material_description=''):
    if not unit_value:
        raise ValueError('Unit/UOM is required')

    normalized = str(unit_value).strip().lower()
    if normalized in UNIT_NORMALIZATION:
        return UNIT_NORMALIZATION[normalized]

    # Use description clues for fuel-specific guessing
    if 'diesel' in normalized or 'diesel' in material_description.lower():
        return 'liters_diesel'
    if 'gasoline' in normalized or 'petrol' in material_description.lower():
        return 'gallons_gasoline'
    if 'gallon' in normalized:
        return 'gallons_diesel'
    if 'liter' in normalized or 'litre' in normalized:
        return 'liters_diesel'

    raise ValueError(f'Unsupported SAP unit: {unit_value}')


def classify_scope(source_subtype, material_description=''):
    if source_subtype:
        normalized = str(source_subtype).strip().lower()
        for keyword, scope in SCOPE_CLASSIFICATION.items():
            if keyword in normalized:
                return scope

    description = str(material_description or '').lower()
    if 'diesel' in description or 'gasoline' in description or 'fuel' in description:
        return 'scope_1'
    if 'procure' in description or 'transport' in description or 'logistics' in description:
        return 'scope_3'

    return 'scope_1'


def compute_suspicion(flags):
    score = 100
    reasons = []

    if flags.get('quantity_invalid'):
        reasons.append('Quantity is missing or non-positive')
        score -= 40
    if flags.get('unit_unknown'):
        reasons.append('Unit could not be normalized')
        score -= 30
    if flags.get('date_invalid'):
        reasons.append('Posting date is invalid or missing')
        score -= 20
    if flags.get('facility_missing'):
        reasons.append('Plant/werk is missing')
        score -= 10

    if score < 0:
        score = 0
    return max(score, 0), reasons


class SAPFuelNormalizer:
    """Normalize SAP fuel/procurement rows into emission records."""

    @classmethod
    def normalize_row(cls, raw_row, organization, normalized_by='system'):
        canonical = canonicalize_row(raw_row.raw_content)

        raw_quantity = canonical.get('quantity')
        raw_unit = canonical.get('unit')
        raw_date = canonical.get('posting_date')
        facility_id = str(canonical.get('facility_id') or canonical.get('plant') or canonical.get('werk') or '').strip()
        material_code = str(canonical.get('material_code') or '').strip()
        material_description = str(canonical.get('material_description') or '').strip()
        source_subtype = str(canonical.get('source_subtype') or '').strip()

        suspicion_flags = {
            'quantity_invalid': False,
            'unit_unknown': False,
            'date_invalid': False,
            'facility_missing': False,
        }

        try:
            quantity = parse_decimal(raw_quantity)
            if quantity <= 0:
                suspicion_flags['quantity_invalid'] = True
        except Exception:
            quantity = Decimal('0')
            suspicion_flags['quantity_invalid'] = True

        try:
            posting_date = parse_sap_date(raw_date)
        except Exception:
            posting_date = None
            suspicion_flags['date_invalid'] = True

        try:
            normalized_unit = normalize_sap_unit(raw_unit, material_description)
        except Exception:
            normalized_unit = None
            suspicion_flags['unit_unknown'] = True

        if not facility_id:
            suspicion_flags['facility_missing'] = True

        scope = classify_scope(source_subtype, material_description)

        if normalized_unit:
            emission_qty, emission_unit, conversion_factor = convert_to_co2e(
                quantity,
                normalized_unit,
                'SAP_FUEL'
            )
        else:
            emission_qty = None
            emission_unit = None
            conversion_factor = None

        confidence_score, suspicion_reasons = compute_suspicion(suspicion_flags)
        is_suspicious = bool(suspicion_reasons)

        notes = []
        if material_code:
            notes.append(f"material_code={material_code}")
        if material_description:
            notes.append(f"description={material_description}")
        if source_subtype:
            notes.append(f"subtype={source_subtype}")
        notes.extend(suspicion_reasons)

        normalized = NormalizedRecord(
            organization=organization,
            source_type='SAP_FUEL',
            raw_data_row=raw_row,
            emission_quantity=emission_qty or Decimal('0'),
            emission_unit=emission_unit or 'kg_CO2e',
            metric_type=scope,
            facility_id=facility_id,
            time_period=posting_date or (datetime.now().date()),
            normalized_by=normalized_by,
            unit_converted_from=raw_unit or '',
            conversion_factor=conversion_factor,
            is_suspicious=is_suspicious,
            confidence_score=confidence_score,
            notes='; '.join(notes),
        )

        return normalized
