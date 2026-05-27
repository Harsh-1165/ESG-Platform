from rest_framework import serializers
from .models import ApprovalRecord, AuditLog


class ApprovalRecordSerializer(serializers.ModelSerializer):
    normalized_record_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = ApprovalRecord
        fields = (
            'id', 'normalized_record', 'normalized_record_detail', 'status',
            'reviewer', 'reviewed_at', 'reviewed_comment', 'rejection_reason',
            'lock_reason', 'created_at', 'updated_at'
        )
    
    def get_normalized_record_detail(self, obj):
        from apps.normalization.serializers import NormalizedRecordListSerializer
        return NormalizedRecordListSerializer(obj.normalized_record).data


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = ('id', 'record_type', 'record_id', 'action', 'old_values', 'new_values', 'user', 'timestamp')
