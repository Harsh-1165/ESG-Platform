from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import RawData, RawDataRow
from .serializers import (
    RawDataSerializer,
    RawDataListSerializer,
    RawDataRowSerializer,
    UploadCSVSerializer,
    RawDataUploadResponseSerializer,
)
from .services import FileUploadService


class RawDataViewSet(viewsets.ModelViewSet):
    """Upload and manage raw data batches"""
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        org_id = self.request.META.get('HTTP_X_ORGANIZATION_ID')
        if org_id:
            return RawData.objects.filter(organization_id=org_id)
        return RawData.objects.none()

    def get_serializer_class(self):
        if self.action == 'list':
            return RawDataListSerializer
        return RawDataSerializer

    @action(detail=False, methods=['POST'])
    def upload(self, request):
        """Upload CSV file and store raw records."""
        serializer = UploadCSVSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        org_id = request.META.get('HTTP_X_ORGANIZATION_ID')
        if not org_id:
            return Response(
                {'error': 'Missing Organization ID in HTTP_X_ORGANIZATION_ID header.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_email = getattr(request.user, 'email', str(request.user))
        file_obj = serializer.validated_data['file']
        source_type = serializer.validated_data['source_type']
        data_source_name = serializer.validated_data.get('data_source_name')
        data_source_external_id = serializer.validated_data.get('data_source_external_id')
        payload_schema_name = serializer.validated_data.get('payload_schema_name', '')
        payload_schema_version = serializer.validated_data.get('payload_schema_version', '')

        try:
            upload_result = FileUploadService.upload_csv(
                organization_id=org_id,
                user_email=user_email,
                file_obj=file_obj,
                source_type=source_type,
                data_source_name=data_source_name,
                data_source_external_id=data_source_external_id,
                payload_schema_name=payload_schema_name,
                payload_schema_version=payload_schema_version,
            )

            response_serializer = RawDataUploadResponseSerializer(data=upload_result)
            response_serializer.is_valid(raise_exception=True)

            status_code = status.HTTP_200_OK if upload_result.get('duplicate') else status.HTTP_201_CREATED
            return Response(response_serializer.data, status=status_code)

        except ValueError as exc:
            return Response({'error': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({'error': 'Upload failed: ' + str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['GET'])
    def rows(self, request, pk=None):
        """Get all rows in batch"""
        raw_data = self.get_object()
        rows = raw_data.rows.all()
        
        # Pagination
        limit = int(request.query_params.get('limit', 50))
        offset = int(request.query_params.get('offset', 0))
        
        paginated_rows = rows[offset:offset + limit]
        serializer = RawDataRowSerializer(paginated_rows, many=True)
        
        return Response({
            'count': rows.count(),
            'limit': limit,
            'offset': offset,
            'results': serializer.data
        })
    
    @action(detail=True, methods=['GET'])
    def row_detail(self, request, pk=None):
        """Get single row detail"""
        raw_data = self.get_object()
        row_id = request.query_params.get('row_id')
        
        try:
            row = raw_data.rows.get(id=row_id)
            serializer = RawDataRowSerializer(row)
            return Response(serializer.data)
        except RawDataRow.DoesNotExist:
            return Response(
                {'error': 'Row not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['PATCH'])
    def flag_row(self, request, pk=None):
        """Flag or unflag a row as suspicious"""
        raw_data = self.get_object()
        row_id = request.data.get('row_id')
        is_flagged = request.data.get('is_flagged', False)
        flag_reason = request.data.get('flag_reason', '')
        
        try:
            row = raw_data.rows.get(id=row_id)
            row.is_flagged = is_flagged
            row.flag_reason = flag_reason
            row.save()
            
            serializer = RawDataRowSerializer(row)
            return Response(serializer.data)
        except RawDataRow.DoesNotExist:
            return Response(
                {'error': 'Row not found'},
                status=status.HTTP_404_NOT_FOUND
            )
