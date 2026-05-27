from decimal import Decimal
from datetime import datetime
from django.utils import timezone

from .models import ValidationFlag


# Thresholds / penalties (tunable per org via settings)
THRESHOLDS = {
    'unusually_high_emission_kg': Decimal('1000000'),  # 1,000,000 kg CO2e
    'unusually_high_kwh': Decimal('1000000'),
}


class ValidationService:
    """Reusable validation service for NormalizedRecord-like objects.

    Methods accept either a Django model instance (NormalizedRecord) or a plain dict
    with expected keys: emission_quantity, emission_unit, metric_type, time_period,
    unit_converted_from, conversion_factor, raw_data_row, source_type.
    """

    @staticmethod
    def _get_field(obj, name, default=None):
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    @classmethod
    def evaluate(cls, normalized):
        """Return list of flag dicts without persisting.

        Each flag dict: {rule_code, reason, severity, penalty}
        """
        flags = []

        # emission quantity
        emission_qty = cls._get_field(normalized, 'emission_quantity', None)
        emission_unit = cls._get_field(normalized, 'emission_unit', None)
        metric_type = cls._get_field(normalized, 'metric_type', None)
        time_period = cls._get_field(normalized, 'time_period', None)
        unit_converted_from = cls._get_field(normalized, 'unit_converted_from', None)
        conversion_factor = cls._get_field(normalized, 'conversion_factor', None)
        raw_row = cls._get_field(normalized, 'raw_data_row', None)
        source_type = cls._get_field(normalized, 'source_type', None)

        # Rule: negative quantities
        try:
            if emission_qty is not None and Decimal(str(emission_qty)) < 0:
                flags.append({
                    'rule_code': 'NEGATIVE_QUANTITY',
                    'reason': 'Emission quantity is negative',
                    'severity': 'critical',
                    'penalty': 50,
                })
        except Exception:
            flags.append({
                'rule_code': 'NEGATIVE_QUANTITY_PARSE_ERROR',
                'reason': 'Emission quantity could not be parsed',
                'severity': 'high',
                'penalty': 40,
            })

        # Rule: missing units
        if not emission_unit:
            flags.append({
                'rule_code': 'MISSING_UNIT',
                'reason': 'Emission unit is missing',
                'severity': 'high',
                'penalty': 40,
            })

        # Rule: zero values that should not be zero
        if emission_qty in (0, '0', 0.0) or (emission_qty is not None and Decimal(str(emission_qty)) == 0):
            # For most scope records, zero is suspicious
            flags.append({
                'rule_code': 'ZERO_VALUE',
                'reason': 'Emission value is zero',
                'severity': 'medium',
                'penalty': 30,
            })

        # Rule: unusually high values
        try:
            if emission_qty is not None:
                # normalize to kg if unit is metric_tons_CO2e
                qty = Decimal(str(emission_qty))
                unit = (emission_unit or '').lower()
                if unit == 'metric_tons_co2e' or unit == 'metric_tons_CO2e' or 'tons' in unit:
                    qty_kg = qty * Decimal('1000')
                else:
                    qty_kg = qty

                if qty_kg > THRESHOLDS['unusually_high_emission_kg']:
                    flags.append({
                        'rule_code': 'UNUSUALLY_HIGH_EMISSION',
                        'reason': f'Emission {qty_kg} kg exceeds threshold',
                        'severity': 'high',
                        'penalty': 40,
                    })
        except Exception:
            pass

        # Rule: malformed dates
        if not time_period:
            flags.append({
                'rule_code': 'MALFORMED_DATE',
                'reason': 'time_period is missing or malformed',
                'severity': 'medium',
                'penalty': 20,
            })

        # Rule: unknown source mappings (no conversion factor)
        if (unit_converted_from in (None, '', [])) or conversion_factor in (None, 0):
            flags.append({
                'rule_code': 'UNKNOWN_SOURCE_MAPPING',
                'reason': 'No conversion factor or source unit mapping available',
                'severity': 'medium',
                'penalty': 20,
            })

        # Rule: missing source reference
        if not raw_row:
            flags.append({
                'rule_code': 'MISSING_SOURCE_REFERENCE',
                'reason': 'No raw_data_row/link to source data',
                'severity': 'critical',
                'penalty': 50,
            })

        # Rule: impossible travel/utility values (domain specific)
        if source_type == 'TRAVEL':
            # if distance-based and > 20000 km, impossible
            try:
                dist = cls._get_field(normalized, 'unit_converted_from', None)
                # distance may be embedded in notes; skip heavy parsing here
                # fallback: check emission quantity magnitude
                if emission_qty is not None and Decimal(str(emission_qty)) > Decimal('10000000'):
                    flags.append({
                        'rule_code': 'IMPOSSIBLE_TRAVEL_VALUE',
                        'reason': 'Travel emission unreasonably large',
                        'severity': 'high',
                        'penalty': 40,
                    })
            except Exception:
                pass
        if source_type == 'UTILITY_ELECTRICITY':
            try:
                # if emission much larger than plausible for a billing period
                if emission_qty is not None and Decimal(str(emission_qty)) > Decimal('1E10'):
                    flags.append({
                        'rule_code': 'IMPOSSIBLE_UTILITY_VALUE',
                        'reason': 'Utility emission unreasonably large',
                        'severity': 'high',
                        'penalty': 40,
                    })
            except Exception:
                pass

        return flags

    @classmethod
    def run_and_persist(cls, normalized_record, user_email=None):
        """Evaluate rules, persist ValidationFlag rows, and update the normalized_record's
        `is_suspicious`, `confidence_score`, and `notes` fields.

        Returns list of created ValidationFlag objects.
        """
        flags = cls.evaluate(normalized_record)
        created_flags = []
        total_penalty = 0

        for f in flags:
            total_penalty += f.get('penalty', 0)
            vf = ValidationFlag.objects.create(
                normalized_record=normalized_record,
                rule_code=f['rule_code'],
                reason=f['reason'],
                severity=f.get('severity', 'medium'),
                created_by=user_email or '',
            )
            created_flags.append(vf)

        # Update normalized_record
        try:
            base_confidence = int(getattr(normalized_record, 'confidence_score', 100) or 100)
            new_confidence = max(0, base_confidence - int(total_penalty))
            normalized_record.confidence_score = new_confidence
            normalized_record.is_suspicious = len(created_flags) > 0

            # Append brief flag summary to notes
            notes = getattr(normalized_record, 'notes', '') or ''
            if created_flags:
                flag_summaries = [f"{f['rule_code']}:{f['reason']}" for f in flags]
                notes = (notes + '\n' if notes else '') + ' | '.join(flag_summaries)
                normalized_record.notes = notes

            normalized_record.save(update_fields=['confidence_score', 'is_suspicious', 'notes'])
        except Exception:
            # Best-effort: do not raise to avoid breaking pipeline
            pass

        return created_flags

    @classmethod
    def override_flag(cls, flag_id, overridden_by, override_reason=None):
        """Analyst override: mark a ValidationFlag as resolved and record resolution details.

        Returns the updated ValidationFlag.
        """
        try:
            vf = ValidationFlag.objects.get(id=flag_id)
        except ValidationFlag.DoesNotExist:
            raise

        vf.resolved = True
        vf.resolved_by = overridden_by
        vf.resolved_at = timezone.now()
        vf.resolution_notes = override_reason or ''
        vf.save(update_fields=['resolved', 'resolved_by', 'resolved_at', 'resolution_notes'])

        # If there are no other open flags on the record, clear is_suspicious
        remaining = ValidationFlag.objects.filter(normalized_record=vf.normalized_record, resolved=False).exists()
        if not remaining:
            nr = vf.normalized_record
            nr.is_suspicious = False
            nr.confidence_score = getattr(nr, 'confidence_score', 100)
            nr.save(update_fields=['is_suspicious', 'confidence_score'])

        return vf
