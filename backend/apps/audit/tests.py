from django.test import TestCase

from apps.audit.models import AuditLog
from apps.audit.utils import log_create, log_update
from apps.core.models import Organization


class AuditUtilsTests(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(name='Audit Org')

    def test_log_create_records_organization_and_record_reference(self):
        entry = log_create(
            organization=self.organization,
            actor='auditor@example.com',
            record=self.organization,
            new_values={'name': 'Audit Org'},
            reason='Test create audit',
        )

        self.assertEqual(entry.organization, self.organization)
        self.assertEqual(entry.action, 'created')
        self.assertEqual(entry.actor, 'auditor@example.com')
        self.assertEqual(entry.record_type, 'Organization')
        self.assertEqual(entry.record_id, str(self.organization.id))
        self.assertEqual(entry.new_values, {'name': 'Audit Org'})

    def test_log_update_records_old_and_new_values(self):
        entry = log_update(
            organization=self.organization,
            actor='auditor@example.com',
            record=self.organization,
            old_values={'name': 'Old Name'},
            new_values={'name': 'Audit Org Updated'},
            reason='Test update audit',
        )

        self.assertEqual(entry.action, 'updated')
        self.assertEqual(entry.old_values, {'name': 'Old Name'})
        self.assertEqual(entry.new_values, {'name': 'Audit Org Updated'})

    def test_audit_log_entries_are_immutable(self):
        entry = AuditLog.objects.create(
            organization=self.organization,
            record_type='Organization',
            record_id=str(self.organization.id),
            action='created',
            actor='auditor@example.com',
            old_values={},
            new_values={},
        )

        entry.new_values = {'name': 'Modified'}
        with self.assertRaises(RuntimeError):
            entry.save()
