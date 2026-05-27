import uuid
from django.db import models
from apps.core.models import Organization


class AuditLog(models.Model):
    """Immutable audit log entry for tenant-scoped actions.

    Tracks: actor, timestamp, action type, old/new values, record reference, and optional reason.

    Immutability: entries are write-only; updates raise an error.
    """

    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('locked', 'Locked'),
        ('unlocked', 'Unlocked'),
        ('comment_created', 'Comment Created'),
        ('normalized', 'Normalized'),
        ('imported', 'Imported'),
        ('deleted', 'Deleted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Tenant context (optional): prefer explicit organization FK for multi-tenant filtering
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='audit_logs', null=True, blank=True)

    # Record reference
    record_type = models.CharField(max_length=128, null=True, blank=True, db_index=True, help_text='Model class name, e.g. NormalizedRecord')
    record_id = models.CharField(max_length=64, null=True, blank=True, db_index=True, help_text='PK of referenced record (stringified)')

    # Action details
    action = models.CharField(max_length=32, choices=ACTION_CHOICES, db_index=True)
    actor = models.CharField(max_length=255, help_text='User email or system name')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Before / after snapshots (JSON) - store minimal diffs or full snapshots depending on usage
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)

    # Optional: why this change occurred
    reason = models.TextField(blank=True)

    # Optional: client IP or request metadata for security traces
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=512, blank=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['organization', 'timestamp']),
            models.Index(fields=['record_type', 'record_id']),
            models.Index(fields=['actor', 'timestamp']),
        ]

    def save(self, *args, **kwargs):
        # Prevent updates to existing entries to enforce immutability
        if not getattr(self, '_state', None) or not getattr(self._state, 'adding', True):
            raise RuntimeError('AuditLog entries are immutable and cannot be modified')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.timestamp.isoformat()} {self.actor} {self.action} ({self.record_type or 'system'})"