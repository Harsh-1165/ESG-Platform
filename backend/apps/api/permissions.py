from rest_framework.permissions import BasePermission


class IsOrgMember(BasePermission):
    """Check if user is member of organization"""
    def has_permission(self, request, view):
        org_id = request.META.get('HTTP_X_ORGANIZATION_ID')
        if not org_id:
            return False
        
        from apps.core.models import OrganizationUser
        return OrganizationUser.objects.filter(
            user=request.user,
            organization_id=org_id,
            is_active=True
        ).exists()
