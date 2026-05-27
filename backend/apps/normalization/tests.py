from decimal import Decimal
from django.test import TestCase

from apps.core.models import Organization
from apps.ingestion.models import RawData, RawDataRow
from apps.normalization.models import NormalizedRecord, ValidationFlag
from apps.normalization.validation import ValidationService


class ValidationServiceTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name='Validation Org')
        self.raw_data = RawData.objects.create(
            organization=self.organization,
            source_type='TRAVEL',
            file_name='travel.csv',
            uploaded_by='validator@example.com',
        )
        self.raw_row = RawDataRow.objects.create(
            raw_data=self.raw_data,
            row_number=1,
            raw_content={'travel_distance_km': 1200},
        )
        self.record = NormalizedRecord.objects.create(
            organization=self.organization,
            source_type='TRAVEL',
            raw_data_row=self.raw_row,
            emission_quantity=Decimal('1500'),
            emission_unit='metric_tons_CO2e',
            metric_type='scope_3',
            facility_id='TRAVEL-FACILITY',
            time_period='2025-01-01',
            normalized_by='validator@example.com',
            unit_converted_from='passenger_km',
            conversion_factor=Decimal('0.0002'),
        )

    def test_evaluate_returns_expected_flags_for_invalid_data(self):
        invalid_payload = {
            'emission_quantity': '-1',
            'emission_unit': '',
            'metric_type': 'scope_1',
            'time_period': None,
            'unit_converted_from': '',
            'conversion_factor': None,
            'raw_data_row': None,
            'source_type': 'TRAVEL',
        }

        flags = ValidationService.evaluate(invalid_payload)
        rule_codes = {flag['rule_code'] for flag in flags}

        self.assertIn('NEGATIVE_QUANTITY', rule_codes)
        self.assertIn('MISSING_UNIT', rule_codes)
        self.assertIn('MALFORMED_DATE', rule_codes)
        self.assertIn('UNKNOWN_SOURCE_MAPPING', rule_codes)
        self.assertIn('MISSING_SOURCE_REFERENCE', rule_codes)

    def test_run_and_persist_creates_validation_flags_and_updates_record(self):
        self.record.emission_quantity = Decimal('0')
        self.record.emission_unit = ''
        self.record.time_period = '2025-01-01'
        self.record.unit_converted_from = ''
        self.record.conversion_factor = None
        self.record.raw_data_row = None
        self.record.save()

        created_flags = ValidationService.run_and_persist(self.record, user_email='analyst@example.com')

        self.record.refresh_from_db()
        self.assertTrue(created_flags)
        self.assertTrue(self.record.is_suspicious)
        self.assertLess(self.record.confidence_score, 100)
        self.assertTrue(ValidationFlag.objects.filter(normalized_record=self.record).exists())

    def test_override_flag_marks_flag_resolved_and_clears_suspicion(self):
        flag = ValidationFlag.objects.create(
            normalized_record=self.record,
            rule_code='TEST_OVERRIDE',
            reason='Test override case',
            severity='low',
            created_by='analyst@example.com',
        )
        self.record.is_suspicious = True
        self.record.confidence_score = 70
        self.record.save()

        resolved_flag = ValidationService.override_flag(flag.id, overridden_by='reviewer@example.com', override_reason='Reviewed and accepted')

        self.assertTrue(resolved_flag.resolved)
        self.assertEqual(resolved_flag.resolved_by, 'reviewer@example.com')
        self.assertFalse(resolved_flag.normalized_record.is_suspicious)
