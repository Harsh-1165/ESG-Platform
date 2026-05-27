from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import NormalizedRecord, StatusLog
from .serializers import NormalizedRecordSerializer, NormalizedRecordListSerializer
from .pipeline import normalize_batch
from .filters import apply_dashboard_filters


class NormalizedRecordViewSet(viewsets.ModelViewSet):
    """View and manage normalized emission records"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        org_id = self.request.META.get('HTTP_X_ORGANIZATION_ID')
        if org_id:
            queryset = NormalizedRecord.objects.filter(organization_id=org_id).select_related('approval', 'raw_data_row')

            queryset = apply_dashboard_filters(queryset, self.request.query_params)

            ordering = self.request.query_params.get('ordering')
            if ordering:
                queryset = queryset.order_by(ordering)
            else:
                queryset = queryset.order_by('-time_period', '-created_at')

            return queryset

        return NormalizedRecord.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NormalizedRecordListSerializer
        return NormalizedRecordSerializer
    
    @action(detail=False, methods=['POST'])
    def normalize_batch(self, request):
        """Start normalization of a batch"""
        batch_id = request.data.get('batch_id')
        
        if not batch_id:
            return Response(
                {'error': 'batch_id required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = normalize_batch(batch_id, request.user.email)
        return Response(results, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['PATCH'])
    def update_record(self, request, pk=None):
        """Update normalized record values"""
        record = self.get_object()

        from apps.approval.models import ApprovalRecord, AuditLog
        from .pipeline import create_status_log

        # Determine approval state and editability
        try:
            approval = ApprovalRecord.objects.get(normalized_record=record)
        except ApprovalRecord.DoesNotExist:
            approval = None

        is_flagged = bool(record.is_suspicious)
        is_pending = (approval.status == ApprovalRecord.STATUS_PENDING) if approval else True
        is_locked = (approval.status == ApprovalRecord.STATUS_LOCKED) if approval else False

        if is_locked:
            return Response({'detail': 'Record is locked and cannot be edited.'}, status=status.HTTP_403_FORBIDDEN)

        if not (is_flagged or is_pending):
            return Response({'detail': 'Only flagged or pending records can be edited.'}, status=status.HTTP_403_FORBIDDEN)

        # capture old values
        old_values = {
            'emission_quantity': str(record.emission_quantity) if record.emission_quantity is not None else None,
            'emission_unit': record.emission_unit,
            'metric_type': record.metric_type,
            'facility_id': record.facility_id,
            'time_period': record.time_period.isoformat() if getattr(record, 'time_period', None) is not None else None,
            'notes': record.notes,
        }

        # apply allowed updates
        editable = ('emission_quantity', 'emission_unit', 'metric_type', 'facility_id', 'time_period', 'notes')
        for key in editable:
            if key in request.data:
                setattr(record, key, request.data[key])

        record.save()

        # Log status change
        create_status_log(
            record,
            'updated',
            old_values=old_values,
            new_values={
                k: (str(getattr(record, k)) if getattr(record, k) is not None else None) for k in old_values.keys()
            },
            user=request.user.email if hasattr(request.user, 'email') else str(request.user)
        )

        # Persist audit log (best-effort)
        try:
            AuditLog.objects.create(
                organization_id=record.organization_id,
                user=request.user.email if hasattr(request.user, 'email') else str(request.user),
                action='updated',
                record_type='NormalizedRecord',
                record_id=str(record.id),
                old_values=old_values,
                new_values={
                    k: (str(getattr(record, k)) if getattr(record, k) is not None else None)
                    for k in old_values.keys()
                },
            )
        except Exception:
            pass

        serializer = self.get_serializer(record)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def history(self, request, pk=None):
        """Get change history for record"""
        record = self.get_object()
        logs = record.status_logs.all()
        
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        paginated_logs = logs[offset:offset + limit]
        
        from .serializers import StatusLogSerializer
        serializer = StatusLogSerializer(paginated_logs, many=True)
        
        return Response({
            'count': logs.count(),
            'limit': limit,
            'offset': offset,
            'results': serializer.data
        })

    @action(detail=True, methods=['POST'])
    def add_comment(self, request, pk=None):
        """Add a review comment to a normalized record"""
        record = self.get_object()
        from .serializers import ReviewCommentSerializer

        data = request.data.copy()
        data['emission_record'] = str(record.id)
        data['organization'] = str(record.organization_id)

        serializer = ReviewCommentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        # create audit log for comment
        try:
            from apps.approval.models import AuditLog
            AuditLog.objects.create(
                organization_id=record.organization_id,
                user=request.user.email if hasattr(request.user, 'email') else str(request.user),
                action='comment_added',
                record_type='NormalizedRecord',
                record_id=str(record.id),
                old_values={},
                new_values={'comment_id': str(comment.id), 'comment_text': comment.comment_text},
            )
        except Exception:
            pass

        return Response(serializer.data, status=status.HTTP_201_CREATED)
