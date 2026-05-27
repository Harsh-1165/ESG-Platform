from django.contrib import admin
from .models import Organization, OrganizationUser


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'created_at')
    search_fields = ('name',)


@admin.register(OrganizationUser)
class OrganizationUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'organization', 'role', 'is_active')
    list_filter = ('role', 'is_active')
