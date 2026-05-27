from django.db import IntegrityError
from django.test import TestCase

from apps.core.models import Organization
from apps.ingestion.models import RawData, RawDataRow


class RawDataModelTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name='Test Organization')
        self.raw_data = RawData.objects.create(
            organization=self.organization,
            source_type='UTILITY_ELECTRICITY',
            file_name='utility.csv',
            uploaded_by='analyst@example.com',
        )

    def test_raw_data_string_representation(self):
        self.assertIn('utility.csv', str(self.raw_data))
        self.assertIn('UTILITY_ELECTRICITY', str(self.raw_data))

    def test_raw_data_row_unique_together_constraint(self):
        RawDataRow.objects.create(
            raw_data=self.raw_data,
            row_number=1,
            raw_content={'meter': 'A1', 'value': 100},
        )

        with self.assertRaises(IntegrityError):
            RawDataRow.objects.create(
                raw_data=self.raw_data,
                row_number=1,
                raw_content={'meter': 'A1', 'value': 200},
            )
