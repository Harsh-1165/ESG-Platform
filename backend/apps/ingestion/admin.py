from django.contrib import admin
from .models import RawData, RawDataRow


@admin.register(RawData)
class RawDataAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'source_type', 'status', 'row_count', 'uploaded_at')
    list_filter = ('source_type', 'status')
    search_fields = ('file_name', 'organization__name')


@admin.register(RawDataRow)
class RawDataRowAdmin(admin.ModelAdmin):
    list_display = ('row_number', 'raw_data', 'is_flagged', 'processing_status')
    list_filter = ('is_flagged', 'processing_status')
