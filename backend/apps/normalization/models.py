import uuid
from django.db import models
from apps.core.models import Organization
from apps.ingestion.models import RawDataRow


class NormalizedRecord(models.Model):
    """Normalized emission record"""
    SOURCE_CHOICES = [
        ('SAP_FUEL', 'SAP Fuel/Procurement'),
        ('UTILITY_ELECTRICITY', 'Utility Electricity'),
        ('TRAVEL', 'Corporate Travel'),
    ]
    
    METRIC_SCOPES = [
        ('scope_1', 'Scope 1: Direct Emissions'),
        ('scope_2', 'Scope 2: Indirect - Energy'),
        ('scope_3', 'Scope 3: Indirect - Other'),
    ]
    
    UNIT_CHOICES = [
        ('kg_CO2e', 'Kilograms CO2e'),
        ('metric_tons_CO2e', 'Metric Tons CO2e'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='normalized_records')
    source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    raw_data_row = models.OneToOneField(RawDataRow, on_delete=models.SET_NULL, null=True, blank=True, related_name='normalized_record')
    
    # Emission data
    emission_quantity = models.DecimalField(max_digits=15, decimal_places=2)
    emission_unit = models.CharField(max_length=50, choices=UNIT_CHOICES, default='kg_CO2e')
    metric_type = models.CharField(max_length=20, choices=METRIC_SCOPES)
    
    # Source details
    facility_id = models.CharField(max_length=255, blank=True)
    time_period = models.DateField()
    
    # Normalization metadata
    normalized_at = models.DateTimeField(auto_now_add=True)
    normalized_by = models.CharField(max_length=255)  # User email
    unit_converted_from = models.CharField(max_length=100, blank=True)
    conversion_factor = models.DecimalField(max_digits=15, decimal_places=6, null=True, blank=True)
    
    # Quality flags
    is_suspicious = models.BooleanField(default=False)
    confidence_score = models.IntegerField(default=100)  # 0-100
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.emission_quantity} {self.emission_unit} ({self.source_type})"


class StatusLog(models.Model):
    """Track edits to normalized records"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    normalized_record = models.ForeignKey(NormalizedRecord, on_delete=models.CASCADE, related_name='status_logs')
    action = models.CharField(max_length=50)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    user = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']


class ValidationFlag(models.Model):
    """Stores validation/flagging results for a NormalizedRecord.

    Allows analysts to review, resolve, or override validation flags.
    """
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    normalized_record = models.ForeignKey(NormalizedRecord, on_delete=models.CASCADE, related_name='validation_flags')
    rule_code = models.CharField(max_length=100, help_text='Short code for the rule, e.g. NEGATIVE_QUANTITY')
    reason = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='medium')
    created_by = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Analyst override / resolution
    resolved = models.BooleanField(default=False, db_index=True)
    resolved_by = models.CharField(max_length=255, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['normalized_record', 'rule_code']),
            models.Index(fields=['resolved', 'created_at']),
        ]

    def __str__(self):
        return f"Flag {self.rule_code} on {self.normalized_record_id} ({'resolved' if self.resolved else 'open'})"


class ReviewComment(models.Model):
    """Comments/feedback during approval workflow (tied to a NormalizedRecord)

    This model records reviewer feedback and decision items for a normalized emission record.
    """

    DECISION_CHOICES = [
        ('comment', 'Just a comment'),
        ('pending', 'Needs decision'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    emission_record = models.ForeignKey(NormalizedRecord, on_delete=models.CASCADE, related_name='review_comments')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='review_comments')

    reviewer_name = models.CharField(max_length=255)
    reviewer_email = models.EmailField()

    comment_text = models.TextField()
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, default='comment', db_index=True)

    requires_revision = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['emission_record', 'created_at']),
            models.Index(fields=['organization', 'decision']),
        ]

    def __str__(self):
        return f"Comment by {self.reviewer_email}: {self.decision}"
