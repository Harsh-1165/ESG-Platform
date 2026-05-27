import uuid
from django.db import models
from apps.normalization.models import NormalizedRecord


class ApprovalRecord(models.Model):
    """Approval workflow for normalized records"""
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_LOCKED = 'locked'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_LOCKED, 'Locked'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    normalized_record = models.OneToOneField(NormalizedRecord, on_delete=models.CASCADE, related_name='approval')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    reviewer = models.CharField(max_length=255, null=True, blank=True)  # User email
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_comment = models.TextField(blank=True)
    
    rejection_reason = models.TextField(blank=True)
    
    lock_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.normalized_record.id} - {self.status}"


class AuditLog(models.Model):
    """Complete audit trail"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('locked', 'Locked'),
        ('comment_added', 'Comment Added'),
    ]
    
    RECORD_TYPES = [
        ('NormalizedRecord', 'NormalizedRecord'),
        ('ApprovalRecord', 'ApprovalRecord'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization_id = models.UUIDField(null=True, blank=True)  # For filtering
    record_type = models.CharField(max_length=100, choices=RECORD_TYPES)
    record_id = models.UUIDField()
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    
    user = models.CharField(max_length=255)  # User email
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['organization_id', 'timestamp']),
            models.Index(fields=['record_type', 'record_id']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.record_type} at {self.timestamp}"
