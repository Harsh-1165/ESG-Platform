import uuid
from django.db import models
from apps.core.models import Organization


class RawData(models.Model):
    """Batch of uploaded raw data"""
    SOURCE_TYPES = [
        ('SAP_FUEL', 'SAP Fuel/Procurement'),
        ('UTILITY_ELECTRICITY', 'Utility Electricity'),
        ('TRAVEL', 'Corporate Travel'),
    ]
    
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='raw_data')
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPES)
    file_name = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64, blank=True, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=255)  # User email or ID
    row_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.file_name} ({self.source_type})"


class RawDataRow(models.Model):
    """Individual row from uploaded file"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('normalized', 'Normalized'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raw_data = models.ForeignKey(RawData, on_delete=models.CASCADE, related_name='rows')
    row_number = models.IntegerField()
    raw_content = models.JSONField()  # Original CSV row as JSON
    validation_errors = models.JSONField(default=list, blank=True)  # List of error messages
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.TextField(blank=True)
    processing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['row_number']
        unique_together = ('raw_data', 'row_number')
    
    def __str__(self):
        return f"Row {self.row_number} - {self.raw_data.file_name}"
