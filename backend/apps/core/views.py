from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Organization, OrganizationUser
from .serializers import OrganizationSerializer, OrganizationUserSerializer


class IsOrgMember(permissions.BasePermission):
    """Check if user is member of organization"""
    def has_object_permission(self, request, view, obj):
        return request.user.org_memberships.filter(organization=obj, is_active=True).exists()


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.filter(active=True)
    serializer_class = OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrgMember]
    
    def get_queryset(self):
        """Return organizations user is member of"""
        return Organization.objects.filter(
            members__user=self.request.user,
            members__is_active=True
        ).distinct()
    
    @action(detail=True, methods=['GET'])
    def members(self, request, pk=None):
        org = self.get_object()
        members = org.members.filter(is_active=True)
        serializer = OrganizationUserSerializer(members, many=True)
        return Response(serializer.data)
