from django.shortcuts import get_object_or_404
from apps.core.models import Organization


class TenantMiddleware:
    """
    Multi-tenancy middleware: extracts organization from header
    and stores in request context.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        org_id = request.META.get('HTTP_X_ORGANIZATION_ID')
        
        if org_id:
            try:
                request.organization = Organization.objects.get(id=org_id)
            except Organization.DoesNotExist:
                request.organization = None
        else:
            request.organization = None
        
        response = self.get_response(request)
        return response
