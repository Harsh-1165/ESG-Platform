from django.contrib import admin
from .models import ApprovalRecord, AuditLog


@admin.register(ApprovalRecord)
class ApprovalRecordAdmin(admin.ModelAdmin):
    list_display = ('normalized_record', 'status', 'reviewer', 'reviewed_at')
    list_filter = ('status', 'reviewed_at')
    search_fields = ('reviewer', 'normalized_record__facility_id')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'record_type', 'user', 'timestamp')
    list_filter = ('action', 'record_type', 'timestamp')
    search_fields = ('user', 'record_id')
