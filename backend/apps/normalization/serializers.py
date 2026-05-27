from rest_framework import serializers
from .models import NormalizedRecord, StatusLog


class StatusLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusLog
        fields = ('id', 'action', 'old_values', 'new_values', 'user', 'timestamp')


class NormalizedRecordSerializer(serializers.ModelSerializer):
    status_logs = StatusLogSerializer(many=True, read_only=True)
    
    class Meta:
        model = NormalizedRecord
        fields = (
            'id', 'source_type', 'emission_quantity', 'emission_unit', 'metric_type',
            'facility_id', 'time_period', 'normalized_at', 'normalized_by',
            'unit_converted_from', 'conversion_factor', 'is_suspicious', 'confidence_score',
            'notes', 'status_logs', 'created_at', 'updated_at'
        )


class NormalizedRecordListSerializer(serializers.ModelSerializer):
    approval_status = serializers.SerializerMethodField()
    approval_reviewer = serializers.SerializerMethodField()

    class Meta:
        model = NormalizedRecord
        fields = (
            'id', 'source_type', 'emission_quantity', 'emission_unit', 'metric_type',
            'facility_id', 'time_period', 'is_suspicious', 'confidence_score',
            'approval_status', 'approval_reviewer',
        )

    def get_approval_status(self, obj):
        return getattr(getattr(obj, 'approval', None), 'status', None)

    def get_approval_reviewer(self, obj):
        return getattr(getattr(obj, 'approval', None), 'reviewer', None)


class ReviewCommentSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ReviewComment

        model = ReviewComment
        fields = ('id', 'emission_record', 'organization', 'reviewer_name', 'reviewer_email', 'comment_text', 'decision', 'requires_revision', 'resolved_at', 'resolution_notes', 'created_at')
