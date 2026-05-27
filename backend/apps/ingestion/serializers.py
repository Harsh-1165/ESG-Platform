from rest_framework import serializers
from .models import RawData, RawDataRow


class RawDataRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawDataRow
        fields = ('id', 'row_number', 'raw_content', 'validation_errors', 'is_flagged', 'flag_reason', 'processing_status', 'created_at')


class RawDataSerializer(serializers.ModelSerializer):
    rows = RawDataRowSerializer(many=True, read_only=True)
    
    class Meta:
        model = RawData
        fields = ('id', 'source_type', 'file_name', 'uploaded_at', 'uploaded_by', 'row_count', 'status', 'metadata', 'rows')


class RawDataListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawData
        fields = ('id', 'source_type', 'file_name', 'uploaded_at', 'uploaded_by', 'row_count', 'status')


class UploadCSVSerializer(serializers.Serializer):
    file = serializers.FileField()
    source_type = serializers.ChoiceField(choices=RawData.SOURCE_TYPES)
    data_source_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    data_source_external_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    payload_schema_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    payload_schema_version = serializers.CharField(max_length=50, required=False, allow_blank=True)


class RawDataUploadResponseSerializer(serializers.Serializer):
    duplicate = serializers.BooleanField()
    upload_id = serializers.UUIDField()
    file_name = serializers.CharField()
    source_type = serializers.CharField()
    data_source_id = serializers.CharField(required=False)
    data_source_name = serializers.CharField(required=False)
    row_count = serializers.IntegerField()
    success_count = serializers.IntegerField(required=False)
    failed_count = serializers.IntegerField(required=False)
    status = serializers.CharField()
    file_hash = serializers.CharField(required=False)
    rows = serializers.ListField(child=serializers.DictField(), required=False)
    message = serializers.CharField()
    existing_upload_id = serializers.CharField(required=False, allow_blank=True)
