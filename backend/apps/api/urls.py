from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.core.views import OrganizationViewSet
from apps.ingestion.views import RawDataViewSet
from apps.normalization.views import NormalizedRecordViewSet
from apps.approval.views import ApprovalRecordViewSet, AuditLogViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'ingestion/batches', RawDataViewSet, basename='raw-data')
router.register(r'normalization/records', NormalizedRecordViewSet, basename='normalized-record')
router.register(r'approval/records', ApprovalRecordViewSet, basename='approval-record')
router.register(r'audit/logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
]
