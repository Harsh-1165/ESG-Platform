from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Organization, OrganizationUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class OrganizationSerializer(serializers.ModelSerializer):
    members_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ('id', 'name', 'active', 'settings', 'created_at', 'members_count')
    
    def get_members_count(self, obj):
        return obj.members.filter(is_active=True).count()


class OrganizationUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = OrganizationUser
        fields = ('id', 'user', 'role', 'joined_at', 'is_active')
