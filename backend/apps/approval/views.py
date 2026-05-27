from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ApprovalRecord, AuditLog
from .serializers import ApprovalRecordSerializer, AuditLogSerializer
from .workflow import approve_record, reject_record, lock_record


class ApprovalRecordViewSet(viewsets.ModelViewSet):
    """Approve/reject normalized records"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ApprovalRecordSerializer
    
    def get_queryset(self):
        org_id = self.request.META.get('HTTP_X_ORGANIZATION_ID')
        if org_id:
            queryset = ApprovalRecord.objects.filter(
                normalized_record__organization_id=org_id
            )
            
            # Filter by status
            status_filter = self.request.query_params.get('status')
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            return queryset
        
        return ApprovalRecord.objects.none()
    
    @action(detail=False, methods=['GET'])
    def pending(self, request):
        """Get pending approvals"""
        pending_records = self.get_queryset().filter(status='pending')
        
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        paginated = pending_records[offset:offset + limit]
        serializer = self.get_serializer(paginated, many=True)
        
        return Response({
            'count': pending_records.count(),
            'limit': limit,
            'offset': offset,
            'results': serializer.data
        })
    
    @action(detail=True, methods=['POST'])
    def approve(self, request, pk=None):
        """Approve a record"""
        record = self.get_object()
        comment = request.data.get('comment', '')
        
        try:
            updated_record = approve_record(record, request.user.email, comment)
            serializer = self.get_serializer(updated_record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['POST'])
    def reject(self, request, pk=None):
        """Reject a record"""
        record = self.get_object()
        reason = request.data.get('reason', '')
        
        try:
            updated_record = reject_record(record, request.user.email, reason)
            serializer = self.get_serializer(updated_record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['POST'])
    def lock(self, request, pk=None):
        """Lock a record (immutable)"""
        record = self.get_object()
        reason = request.data.get('reason', '')
        
        try:
            updated_record = lock_record(record, request.user.email, reason)
            serializer = self.get_serializer(updated_record)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """View audit logs"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AuditLogSerializer
    
    def get_queryset(self):
        org_id = self.request.META.get('HTTP_X_ORGANIZATION_ID')
        if org_id:
            queryset = AuditLog.objects.filter(organization_id=org_id)
            
            # Filters
            action = self.request.query_params.get('action')
            if action:
                queryset = queryset.filter(action=action)
            
            record_type = self.request.query_params.get('record_type')
            if record_type:
                queryset = queryset.filter(record_type=record_type)
            
            return queryset
        
        return AuditLog.objects.none()
