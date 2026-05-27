from decimal import Decimal
from datetime import datetime

from apps.normalization.units import convert_to_co2e
from .models import NormalizedRecord


UTILITY_HEADER_MAP = {
    'meter id': 'meter_id',
    'meter': 'meter_id',
    'meter_number': 'meter_id',

    'billing start date': 'billing_start',
    'billing_start': 'billing_start',
    'start date': 'billing_start',

    'billing end date': 'billing_end',
    'billing_end': 'billing_end',
    'end date': 'billing_end',

    'kwh': 'consumption',
    'consumption': 'consumption',
    'usage': 'consumption',
    'energy': 'consumption',

    'tariff': 'tariff',
    'site': 'site',
    'location': 'site',
    'invoice number': 'invoice_number',
    'invoice_no': 'invoice_number',
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

UNIT_ALIASES = {
    'kwh': 'kWh',
    'mwh': 'MWh',
    'kilo watt hour': 'kWh',
    'kilowatt-hour': 'kWh',
}

LARGE_USAGE_THRESHOLD_KWH = Decimal('1000000')  # 1,000,000 kWh ~= 1 GWh (tunable)


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
        canonical_key = UTILITY_HEADER_MAP.get(key, key)
        canonical[canonical_key] = value
    return canonical


def parse_date(value):
    if value is None or str(value).strip() == '':
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, str):
        cleaned = value.strip()
        for fmt in DATE_FORMATS:
            try:
                return datetime.strptime(cleaned, fmt).date()
            except ValueError:
                continue
    # Last-resort: try ISO parse
    try:
        return datetime.fromisoformat(str(value)).date()
    except Exception:
        return None


def parse_decimal(value):
    if value is None:
        raise ValueError('Missing consumption')
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    if isinstance(value, str):
        cleaned = value.strip().replace(' ', '')
        if cleaned.count(',') and not cleaned.count('.'):
            cleaned = cleaned.replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
        return Decimal(cleaned)
    raise ValueError(f'Unsupported consumption format: {value}')


def normalize_unit(unit_value):
    if not unit_value:
        return 'kWh'
    u = str(unit_value).strip().lower()
    if u in UNIT_ALIASES:
        return UNIT_ALIASES[u]
    if 'kwh' in u:
        return 'kWh'
    if 'mwh' in u or 'mwh' in u.upper():
        return 'MWh'
    return 'kWh'


class UtilityNormalizer:
    """Normalize utility electricity billing rows into normalized emission records."""

    @classmethod
    def normalize_row(cls, raw_row, organization, normalized_by='system'):
        canonical = canonicalize_row(raw_row.raw_content)

        meter_id = str(canonical.get('meter_id') or '').strip()
        billing_start = canonical.get('billing_start')
        billing_end = canonical.get('billing_end')
        raw_consumption = canonical.get('consumption') or canonical.get('kwh')
        unit_hint = canonical.get('unit') or canonical.get('uom') or ''
        site = str(canonical.get('site') or canonical.get('location') or '').strip()
        invoice_no = str(canonical.get('invoice_number') or '')
        tariff = str(canonical.get('tariff') or '')

        # Parse consumption
        suspicion_flags = {
            'negative_usage': False,
            'missing_meter': False,
            'large_usage': False,
            'date_invalid': False,
        }

        try:
            consumption = parse_decimal(raw_consumption)
            if consumption < 0:
                suspicion_flags['negative_usage'] = True
        except Exception:
            consumption = Decimal('0')
            suspicion_flags['date_invalid'] = True

        # Parse dates
        start_date = parse_date(billing_start)
        end_date = parse_date(billing_end)
        if not start_date or not end_date:
            # If only one present, use it as period end
            if start_date and not end_date:
                end_date = start_date
            elif end_date and not start_date:
                start_date = end_date
            else:
                suspicion_flags['date_invalid'] = True
                # fallback to today
                end_date = datetime.now().date()
                start_date = end_date

        # Normalize unit and convert consumption to kWh if needed
        unit_normalized = normalize_unit(unit_hint)
        try:
            if unit_normalized == 'MWh':
                consumption_kwh = consumption * Decimal('1000')
            else:
                consumption_kwh = consumption
        except Exception:
            consumption_kwh = Decimal('0')

        # Flag missing meter id
        if not meter_id:
            suspicion_flags['missing_meter'] = True

        # Flag large usage
        if consumption_kwh > LARGE_USAGE_THRESHOLD_KWH:
            suspicion_flags['large_usage'] = True

        # Classify as scope 2
        scope = 'scope_2'

        # Convert to CO2e using common conversion factors
        try:
            emission_qty, emission_unit, conversion_factor = convert_to_co2e(
                consumption_kwh,
                'kWh',
                'UTILITY_ELECTRICITY'
            )
        except Exception:
            emission_qty = None
            emission_unit = None
            conversion_factor = None

        # Compute daily average if period > 0
        days = (end_date - start_date).days + 1
        daily_kwh = None
        if days > 0:
            daily_kwh = (consumption_kwh / Decimal(days)).quantize(Decimal('0.01'))

        # Compute confidence and reasons
        reasons = []
        confidence = 100
        if suspicion_flags['negative_usage']:
            reasons.append('Negative usage')
            confidence -= 50
        if suspicion_flags['missing_meter']:
            reasons.append('Missing meter id')
            confidence -= 30
        if suspicion_flags['large_usage']:
            reasons.append('Unusually large consumption')
            confidence -= 20
        if suspicion_flags['date_invalid']:
            reasons.append('Invalid billing dates')
            confidence -= 20
        confidence = max(confidence, 0)
        is_suspicious = len(reasons) > 0

        notes = []
        notes.append(f"invoice={invoice_no}")
        notes.append(f"tariff={tariff}")
        notes.append(f"period_start={start_date}")
        notes.append(f"period_end={end_date}")
        if daily_kwh is not None:
            notes.append(f"daily_kwh={daily_kwh}")

        normalized = NormalizedRecord(
            organization=organization,
            source_type='UTILITY_ELECTRICITY',
            raw_data_row=raw_row,
            emission_quantity=emission_qty or Decimal('0'),
            emission_unit=emission_unit or 'kg_CO2e',
            metric_type=scope,
            facility_id=site or meter_id,
            time_period=end_date,
            normalized_by=normalized_by,
            unit_converted_from=unit_normalized,
            conversion_factor=conversion_factor,
            is_suspicious=is_suspicious,
            confidence_score=confidence,
            notes='; '.join(notes),
        )

        return normalized
