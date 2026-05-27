import hashlib
import json
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    """Multi-tenant organization entity"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True, db_index=True)
    settings = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['active', 'created_at']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name


class OrganizationUser(models.Model):
    """Link users to organizations with roles"""
    ROLES = [
        ('admin', 'Administrator'),
        ('analyst', 'Analyst'),
        ('viewer', 'Viewer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='org_memberships')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, choices=ROLES, default='viewer')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'organization')

    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"


class DataSource(models.Model):
    SOURCE_TYPES = [
        ('SAP_FUEL', 'SAP Fuel/Procurement'),
        ('UTILITY_ELECTRICITY', 'Utility Electricity'),
        ('TRAVEL', 'Corporate Travel'),
    ]

    IMPORT_FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('manual', 'Manual'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='data_sources')
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES, db_index=True)
    external_id = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_person = models.CharField(max_length=255, blank=True)
    last_import_at = models.DateTimeField(null=True, blank=True)
    import_frequency = models.CharField(max_length=20, choices=IMPORT_FREQUENCIES, default='manual')
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('organization', 'name')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'source_type']),
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['organization', 'external_id']),
        ]

    def __str__(self):
        return f"{self.organization.name} - {self.name}"


class RawRecord(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('imported', 'Imported'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
        ('superseded', 'Superseded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='raw_records')
    data_source = models.ForeignKey(DataSource, on_delete=models.PROTECT, related_name='raw_records')
    raw_payload = models.JSONField(help_text='Original JSON payload from the source system')
    raw_payload_hash = models.CharField(max_length=64, db_index=True, editable=False)
    external_id = models.CharField(max_length=500, db_index=True, help_text='Source system record ID')
    external_timestamp = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received', db_index=True)
    import_timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    import_batch_id = models.CharField(max_length=255, blank=True, db_index=True)
    import_errors = models.JSONField(default=list, blank=True)
    processing_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=255)

    class Meta:
        unique_together = ('organization', 'data_source', 'external_id')
        ordering = ['-import_timestamp']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'data_source', 'status']),
            models.Index(fields=['external_id']),
            models.Index(fields=['import_batch_id']),
            models.Index(fields=['raw_payload_hash']),
        ]

    def clean(self):
        if not self.external_id:
            raise ValidationError({'external_id': 'external_id is required for RawRecord.'})
        if self.raw_payload is None:
            raise ValidationError({'raw_payload': 'raw_payload cannot be null.'})

    def save(self, *args, **kwargs):
        if self.raw_payload is not None:
            payload_bytes = json.dumps(self.raw_payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
            self.raw_payload_hash = hashlib.sha256(payload_bytes).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"RawRecord({self.external_id}) [{self.status}]"
