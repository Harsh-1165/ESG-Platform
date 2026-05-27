from django.contrib import admin
from .models import NormalizedRecord, StatusLog


@admin.register(NormalizedRecord)
class NormalizedRecordAdmin(admin.ModelAdmin):
    list_display = ('emission_quantity', 'source_type', 'metric_type', 'confidence_score', 'is_suspicious', 'normalized_at')
    list_filter = ('source_type', 'metric_type', 'is_suspicious', 'confidence_score')
    search_fields = ('facility_id', 'organization__name')


@admin.register(StatusLog)
class StatusLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'timestamp')
    list_filter = ('action', 'timestamp')
