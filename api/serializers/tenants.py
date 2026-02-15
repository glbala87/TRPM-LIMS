"""
Serializers for tenants app models.
"""
from rest_framework import serializers
from tenants.models import Organization, Laboratory, OrganizationMembership, LaboratoryMembership


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model."""
    laboratory_count = serializers.ReadOnlyField()
    user_count = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = [
            'id', 'uid', 'code', 'name', 'description',
            'address', 'city', 'state', 'country', 'postal_code',
            'phone', 'email', 'website',
            'subscription_tier', 'max_laboratories', 'max_users', 'max_samples_per_month',
            'laboratory_count', 'user_count', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uid', 'laboratory_count', 'user_count', 'created_at', 'updated_at']


class OrganizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Organization list views."""
    laboratory_count = serializers.ReadOnlyField()
    user_count = serializers.ReadOnlyField()

    class Meta:
        model = Organization
        fields = ['id', 'uid', 'code', 'name', 'subscription_tier', 'laboratory_count', 'user_count', 'is_active']


class LaboratorySerializer(serializers.ModelSerializer):
    """Serializer for Laboratory model."""
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Laboratory
        fields = [
            'id', 'uid', 'organization', 'organization_name', 'code', 'name', 'description',
            'lab_type', 'accreditation_number', 'accreditation_body', 'accreditation_expiry',
            'address', 'phone', 'email', 'timezone', 'features_enabled',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'uid', 'created_at', 'updated_at']


class LaboratoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Laboratory list views."""
    organization_code = serializers.CharField(source='organization.code', read_only=True)

    class Meta:
        model = Laboratory
        fields = ['id', 'uid', 'code', 'name', 'organization_code', 'lab_type', 'is_active']


class OrganizationMembershipSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationMembership model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = OrganizationMembership
        fields = ['id', 'user', 'user_name', 'organization', 'organization_name', 'role', 'is_active', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class LaboratoryMembershipSerializer(serializers.ModelSerializer):
    """Serializer for LaboratoryMembership model."""
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    laboratory_name = serializers.CharField(source='laboratory.name', read_only=True)

    class Meta:
        model = LaboratoryMembership
        fields = [
            'id', 'user', 'user_name', 'laboratory', 'laboratory_name',
            'role', 'department', 'is_active', 'is_default', 'joined_at'
        ]
        read_only_fields = ['id', 'joined_at']
