from decimal import Decimal
from datetime import datetime

from apps.normalization.units import convert_to_co2e
from .models import NormalizedRecord


TRAVEL_HEADER_MAP = {
    'employee': 'employee',
    'person': 'employee',

    'category': 'category',
    'trip type': 'category',

    'origin': 'origin',
    'from': 'origin',

    'destination': 'destination',
    'to': 'destination',

    'origin airport': 'origin_airport',
    'destination airport': 'destination_airport',
    'origin_iata': 'origin_airport',
    'dest_iata': 'destination_airport',

    'distance': 'distance',
    'distance_km': 'distance',
    'km': 'distance',

    'trip date': 'trip_date',
    'date': 'trip_date',

    'class': 'cabin_class',
    'cabin': 'cabin_class',
}

# simple airport-to-distance lookup (placeholder)
# in production, use a geolocation/OSM or a commercial provider
AIRPORT_DISTANCE_ESTIMATES_KM = {
    ('JFK', 'LHR'): 5540,
    ('LHR', 'JFK'): 5540,
    ('SFO', 'LAX'): 543,
    ('LAX', 'SFO'): 543,
}

DATE_FORMATS = [
    '%Y-%m-%d',
    '%d/%m/%Y',
    '%d.%m.%Y',
    '%m/%d/%Y',
    '%Y%m%d',
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
        canonical_key = TRAVEL_HEADER_MAP.get(key, key)
        canonical[canonical_key] = value
    return canonical


def parse_decimal(value):
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    if isinstance(value, str):
        cleaned = value.strip().replace(' ', '')
        if cleaned.count(',') and not cleaned.count('.'):
            cleaned = cleaned.replace(',', '.')
        else:
            cleaned = cleaned.replace(',', '')
        try:
            return Decimal(cleaned)
        except Exception:
            return None
    return None


def parse_date(value):
    if value is None:
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
    try:
        return datetime.fromisoformat(str(value)).date()
    except Exception:
        return None


def estimate_distance_from_airports(orig_code, dest_code):
    if not orig_code or not dest_code:
        return None
    key = (str(orig_code).strip().upper(), str(dest_code).strip().upper())
    return AIRPORT_DISTANCE_ESTIMATES_KM.get(key)


class TravelNormalizer:
    """Normalize corporate travel rows into normalized emission records."""

    @classmethod
    def normalize_row(cls, raw_row, organization, normalized_by='system'):
        canonical = canonicalize_row(raw_row.raw_content)

        employee = str(canonical.get('employee') or '').strip()
        category = str(canonical.get('category') or '').strip().lower()  # flight, hotel, taxi, rail
        origin = str(canonical.get('origin') or '').strip()
        destination = str(canonical.get('destination') or '').strip()
        origin_airport = str(canonical.get('origin_airport') or '').strip().upper()
        destination_airport = str(canonical.get('destination_airport') or '').strip().upper()
        raw_distance = canonical.get('distance')
        cabin_class = str(canonical.get('cabin_class') or '').strip().lower()
        trip_date_raw = canonical.get('trip_date')

        suspicion_flags = {
            'missing_origin_dest': False,
            'invalid_airports': False,
            'distance_missing': False,
        }

        # parse distance if provided
        distance_km = parse_decimal(raw_distance)

        # if no numeric distance and airport codes exist, try estimate
        if distance_km is None and origin_airport and destination_airport:
            est = estimate_distance_from_airports(origin_airport, destination_airport)
            if est:
                distance_km = Decimal(est)
        # If still none, set flag for missing distance for certain categories
        if distance_km is None and category in ('flight', 'rail', 'taxi'):
            suspicion_flags['distance_missing'] = True

        # parse trip date
        trip_date = parse_date(trip_date_raw)
        if trip_date is None:
            trip_date = datetime.now().date()

        # rules for missing origin/destination
        if not origin and not origin_airport:
            suspicion_flags['missing_origin_dest'] = True
        if not destination and not destination_airport:
            suspicion_flags['missing_origin_dest'] = True

        # basic airport validation: must be 3-letter codes
        if (origin_airport and len(origin_airport) != 3) or (destination_airport and len(destination_airport) != 3):
            suspicion_flags['invalid_airports'] = True

        # estimate emissions
        emission_qty = None
        emission_unit = None
        conversion_factor = None

        try:
            if category == 'flight' and distance_km is not None:
                # simple emission factor per km for passenger flights (kg CO2e per passenger km)
                # example factor 0.255 kg/km (placeholder)
                factor = Decimal('0.255')
                emission_kg = distance_km * factor
                # class multiplier: business class assumed 1.5x, first class 2x
                if 'business' in cabin_class:
                    emission_kg *= Decimal('1.5')
                if 'first' in cabin_class:
                    emission_kg *= Decimal('2')
                emission_qty = emission_kg.quantize(Decimal('0.01'))
                emission_unit = 'kg_CO2e'
                conversion_factor = factor
            elif category in ('taxi', 'car') and distance_km is not None:
                # simple taxi factor (kg CO2e per km)
                factor = Decimal('0.192')
                emission_kg = distance_km * factor
                emission_qty = emission_kg.quantize(Decimal('0.01'))
                emission_unit = 'kg_CO2e'
                conversion_factor = factor
            elif category == 'rail' and distance_km is not None:
                factor = Decimal('0.041')
                emission_kg = distance_km * factor
                emission_qty = emission_kg.quantize(Decimal('0.01'))
                emission_unit = 'kg_CO2e'
                conversion_factor = factor
            elif category == 'hotel':
                # hotel emissions: estimate per night if distance absent; placeholder 15 kg/night
                factor = Decimal('15')
                emission_kg = factor
                emission_qty = emission_kg.quantize(Decimal('0.01'))
                emission_unit = 'kg_CO2e'
                conversion_factor = factor
            else:
                # fallback: no emission computed
                emission_qty = Decimal('0')
                emission_unit = 'kg_CO2e'
                conversion_factor = None
        except Exception:
            emission_qty = Decimal('0')
            emission_unit = 'kg_CO2e'
            conversion_factor = None

        # compute confidence and reasons
        reasons = []
        confidence = 100
        if suspicion_flags['missing_origin_dest']:
            reasons.append('Missing origin or destination')
            confidence -= 40
        if suspicion_flags['invalid_airports']:
            reasons.append('Invalid airport codes')
            confidence -= 30
        if suspicion_flags['distance_missing']:
            reasons.append('Distance missing; estimated or none')
            confidence -= 20
        confidence = max(confidence, 0)
        is_suspicious = len(reasons) > 0

        notes = []
        if employee:
            notes.append(f"employee={employee}")
        notes.append(f"category={category}")
        if origin_airport and destination_airport:
            notes.append(f"airports={origin_airport}-{destination_airport}")
        if distance_km is not None:
            notes.append(f"distance_km={distance_km}")
        if trip_date:
            notes.append(f"trip_date={trip_date}")

        normalized = NormalizedRecord(
            organization=organization,
            source_type='TRAVEL',
            raw_data_row=raw_row,
            emission_quantity=emission_qty or Decimal('0'),
            emission_unit=emission_unit or 'kg_CO2e',
            metric_type='scope_3',
            facility_id=employee or '',
            time_period=trip_date,
            normalized_by=normalized_by,
            unit_converted_from='km' if distance_km is not None else '',
            conversion_factor=conversion_factor,
            is_suspicious=is_suspicious,
            confidence_score=confidence,
            notes='; '.join(notes),
        )

        return normalized
