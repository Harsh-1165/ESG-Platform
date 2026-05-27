from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from apps.core.models import Organization
from apps.ingestion.models import RawData, RawDataRow
from apps.normalization.models import NormalizedRecord
from apps.approval.models import ApprovalRecord, AuditLog


class ApiWorkflowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='api_test_user',
            email='api_test@example.com',
            password='secret123'
        )
        self.organization = Organization.objects.create(name='API Org')
        self.client.force_authenticate(user=self.user)
        self.org_header = {'HTTP_X_ORGANIZATION_ID': str(self.organization.id)}

    def test_full_ingestion_normalization_and_approval_flow(self):
        csv_content = (
            'category,origin_airport,destination_airport,trip_date,cabin_class\n'
            'flight,JFK,LHR,2025-07-01,business\n'
        )
        upload_file = SimpleUploadedFile(
            'travel.csv',
            csv_content.encode('utf-8'),
            content_type='text/csv'
        )

        response = self.client.post(
            '/api/ingestion/batches/upload/',
            {
                'file': upload_file,
                'source_type': 'TRAVEL',
            },
            format='multipart',
            **self.org_header
        )

        self.assertEqual(response.status_code, 201)
        batch_id = response.data['upload_id']
        batch = RawData.objects.get(id=batch_id)
        self.assertEqual(batch.organization, self.organization)
        self.assertEqual(batch.row_count, 1)
        self.assertEqual(batch.status, 'completed')
        self.assertEqual(batch.rows.count(), 1)

        row = batch.rows.first()
        self.assertFalse(row.is_flagged)

        response = self.client.get(
            f'/api/ingestion/batches/{batch_id}/rows/',
            format='json',
            **self.org_header
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        response = self.client.patch(
            f'/api/ingestion/batches/{batch_id}/flag_row/',
            {
                'row_id': str(row.id),
                'is_flagged': True,
                'flag_reason': 'Test suspicion',
            },
            format='json',
            **self.org_header
        )
        self.assertEqual(response.status_code, 200)
        row.refresh_from_db()
        self.assertTrue(row.is_flagged)
        self.assertEqual(row.flag_reason, 'Test suspicion')

        response = self.client.post(
            '/api/normalization/records/normalize_batch/',
            {'batch_id': batch_id},
            format='json',
            **self.org_header
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['created'], 1)
        self.assertEqual(response.data['failed'], 0)

        record = NormalizedRecord.objects.filter(organization=self.organization).first()
        self.assertIsNotNone(record)
        self.assertTrue(record.emission_quantity > 0)

        response = self.client.patch(
            f'/api/normalization/records/{record.id}/update_record/',
            {'notes': 'Corrected after review'},
            format='json',
            **self.org_header
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['notes'], 'Corrected after review')

        approval = ApprovalRecord.objects.filter(normalized_record=record).first()
        self.assertIsNotNone(approval)
        self.assertEqual(approval.status, 'pending')

        response = self.client.get(
            '/api/approval/records/pending/',
            format='json',
            **self.org_header
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)

        response = self.client.post(
            f'/api/approval/records/{approval.id}/approve/',
            {'comment': 'Looks good'},
            format='json',
            **self.org_header
        )
        self.assertEqual(response.status_code, 200)
        approval.refresh_from_db()
        self.assertEqual(approval.status, 'approved')
        self.assertEqual(approval.reviewer, self.user.email)

        response = self.client.post(
            f'/api/approval/records/{approval.id}/lock/',
            {'reason': 'Finalized'},
            format='json',
            **self.org_header
        )
        self.assertEqual(response.status_code, 200)
        approval.refresh_from_db()
        self.assertEqual(approval.status, 'locked')
        self.assertEqual(approval.lock_reason, 'Finalized')

        response = self.client.get(
            '/api/audit/logs/?record_type=ApprovalRecord',
            format='json',
            **self.org_header
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['results'])
        self.assertTrue(AuditLog.objects.filter(record_id=approval.id, action='approved').exists())
        self.assertTrue(AuditLog.objects.filter(record_id=approval.id, action='locked').exists())
