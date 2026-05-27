from decimal import Decimal
from django.test import TestCase

from apps.core.models import Organization
from apps.ingestion.models import RawData, RawDataRow
from apps.normalization.models import NormalizedRecord
from apps.approval.models import ApprovalRecord, AuditLog
from apps.approval.workflow import approve_record, can_transition, lock_record, reject_record


class ApprovalWorkflowTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name='Approval Org')
        self.raw_data = RawData.objects.create(
            organization=self.organization,
            source_type='TRAVEL',
            file_name='approval.csv',
            uploaded_by='approver@example.com',
        )
        self.raw_row = RawDataRow.objects.create(
            raw_data=self.raw_data,
            row_number=1,
            raw_content={'travel_distance_km': 1500},
            processing_status='normalized',
        )
        self.normalized_record = NormalizedRecord.objects.create(
            organization=self.organization,
            source_type='TRAVEL',
            raw_data_row=self.raw_row,
            emission_quantity=Decimal('2500'),
            emission_unit='metric_tons_CO2e',
            metric_type='scope_3',
            facility_id='APPROVAL-FACILITY',
            time_period='2025-06-01',
            normalized_by='approver@example.com',
            unit_converted_from='passenger_km',
            conversion_factor=Decimal('0.0002'),
        )
        self.approval_record = ApprovalRecord.objects.create(normalized_record=self.normalized_record)

    def test_can_transition_defines_valid_workflow(self):
        self.assertTrue(can_transition('pending', 'approved'))
        self.assertTrue(can_transition('approved', 'locked'))
        self.assertFalse(can_transition('approved', 'rejected'))
        self.assertFalse(can_transition('locked', 'approved'))

    def test_approve_record_changes_status_and_creates_audit_log(self):
        approved = approve_record(self.approval_record, reviewer_email='reviewer@example.com', comment='Looks good')

        self.assertEqual(approved.status, 'approved')
        self.assertEqual(approved.reviewer, 'reviewer@example.com')
        self.assertEqual(approved.reviewed_comment, 'Looks good')
        self.assertIsNotNone(approved.reviewed_at)

        audit = AuditLog.objects.filter(record_id=approved.id, action='approved').first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.old_values.get('status'), 'pending')
        self.assertEqual(audit.new_values.get('status'), 'approved')

    def test_reject_record_changes_status_resets_raw_row_and_logs_audit(self):
        rejected = reject_record(self.approval_record, reviewer_email='reviewer@example.com', reason='Incorrect conversion')

        self.assertEqual(rejected.status, 'rejected')
        self.assertEqual(rejected.reviewer, 'reviewer@example.com')
        self.assertEqual(rejected.rejection_reason, 'Incorrect conversion')
        self.assertEqual(rejected.normalized_record.raw_data_row.processing_status, 'pending')

        audit = AuditLog.objects.filter(record_id=rejected.id, action='rejected').first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.old_values.get('status'), 'pending')
        self.assertEqual(audit.new_values.get('status'), 'rejected')

    def test_lock_record_changes_status_and_logs_audit(self):
        approved = approve_record(self.approval_record, reviewer_email='reviewer@example.com', comment='Ready to lock')
        locked = lock_record(approved, admin_email='admin@example.com', reason='Finalized for reporting')

        self.assertEqual(locked.status, 'locked')
        self.assertEqual(locked.lock_reason, 'Finalized for reporting')

        audit = AuditLog.objects.filter(record_id=locked.id, action='locked').first()
        self.assertIsNotNone(audit)
        self.assertEqual(audit.old_values.get('status'), 'approved')
        self.assertEqual(audit.new_values.get('status'), 'locked')

    def test_invalid_transition_raises_value_error(self):
        self.approval_record.status = 'approved'
        self.approval_record.save()

        with self.assertRaises(ValueError):
            approve_record(self.approval_record, reviewer_email='reviewer@example.com')
