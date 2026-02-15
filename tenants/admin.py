# tenants/admin.py

from django.contrib import admin
from .models import Organization, Laboratory, OrganizationMembership, LaboratoryMembership


class LaboratoryInline(admin.TabularInline):
    model = Laboratory
    extra = 0
    fields = ['code', 'name', 'lab_type', 'is_active']


class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    fields = ['user', 'role', 'is_active']


class LaboratoryMembershipInline(admin.TabularInline):
    model = LaboratoryMembership
    extra = 0
    fields = ['user', 'role', 'department', 'is_default', 'is_active']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'subscription_tier', 'laboratory_count', 'user_count', 'is_active']
    list_filter = ['subscription_tier', 'is_active', 'country']
    search_fields = ['code', 'name', 'email']
    readonly_fields = ['uid', 'created_at', 'updated_at']
    inlines = [LaboratoryInline, OrganizationMembershipInline]

    fieldsets = (
        (None, {
            'fields': ('uid', 'code', 'name', 'description')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code', 'phone', 'email', 'website')
        }),
        ('Subscription', {
            'fields': ('subscription_tier', 'max_laboratories', 'max_users', 'max_samples_per_month')
        }),
        ('Settings', {
            'fields': ('settings', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Laboratory)
class LaboratoryAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'organization', 'lab_type', 'is_active']
    list_filter = ['lab_type', 'is_active', 'organization']
    search_fields = ['code', 'name', 'organization__name']
    readonly_fields = ['uid', 'created_at', 'updated_at']
    inlines = [LaboratoryMembershipInline]

    fieldsets = (
        (None, {
            'fields': ('uid', 'organization', 'code', 'name', 'description', 'lab_type')
        }),
        ('Accreditation', {
            'fields': ('accreditation_number', 'accreditation_body', 'accreditation_expiry')
        }),
        ('Contact Information', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Settings', {
            'fields': ('settings', 'timezone', 'features_enabled', 'is_active'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'organization']
    search_fields = ['user__username', 'organization__name']


@admin.register(LaboratoryMembership)
class LaboratoryMembershipAdmin(admin.ModelAdmin):
    list_display = ['user', 'laboratory', 'role', 'department', 'is_default', 'is_active']
    list_filter = ['role', 'is_active', 'laboratory__organization', 'laboratory']
    search_fields = ['user__username', 'laboratory__name']
