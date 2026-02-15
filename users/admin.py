"""
Admin configuration for the users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Role, UserProfile, UserSession


class UserProfileInline(admin.StackedInline):
    """Inline for UserProfile in User admin."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'LIMS Profile'
    fieldsets = (
        ('Role & Department', {
            'fields': ('role', 'department', 'title', 'employee_id')
        }),
        ('Contact', {
            'fields': ('phone', 'extension')
        }),
        ('Permissions Override', {
            'fields': ('can_approve_results', 'can_release_reports'),
            'classes': ('collapse',)
        }),
        ('Account Status', {
            'fields': ('is_active_lims', 'is_locked', 'login_attempts', 'require_password_change'),
        }),
        ('Qualifications', {
            'fields': ('qualifications', 'signature_image'),
            'classes': ('collapse',)
        }),
    )


class UserAdmin(BaseUserAdmin):
    """Extended User admin with UserProfile inline."""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_role')
    list_filter = BaseUserAdmin.list_filter + ('userprofile__role',)

    def get_role(self, obj):
        if hasattr(obj, 'userprofile') and obj.userprofile.role:
            return obj.userprofile.role.display_name
        return '-'
    get_role.short_description = 'LIMS Role'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin for Role model."""
    list_display = ('display_name', 'name', 'is_active', 'get_permission_summary')
    list_filter = ('is_active',)
    search_fields = ('name', 'display_name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'description', 'is_active')
        }),
        ('Patient Permissions', {
            'fields': ('can_view_patients', 'can_edit_patients', 'can_create_patients'),
            'classes': ('collapse',)
        }),
        ('Sample Permissions', {
            'fields': ('can_view_samples', 'can_edit_samples', 'can_create_samples', 'can_delete_samples'),
            'classes': ('collapse',)
        }),
        ('Result Permissions', {
            'fields': ('can_view_results', 'can_enter_results', 'can_review_results',
                       'can_approve_results', 'can_release_reports'),
            'classes': ('collapse',)
        }),
        ('Management Permissions', {
            'fields': ('can_manage_equipment', 'can_manage_reagents', 'can_manage_storage'),
            'classes': ('collapse',)
        }),
        ('Data Permissions', {
            'fields': ('can_view_analytics', 'can_export_data', 'can_import_data'),
            'classes': ('collapse',)
        }),
        ('Admin Permissions', {
            'fields': ('can_manage_users', 'can_view_audit_logs', 'can_configure_system'),
            'classes': ('collapse',)
        }),
        ('Django Permissions', {
            'fields': ('permissions',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    filter_horizontal = ('permissions',)

    def get_permission_summary(self, obj):
        """Show a summary of key permissions."""
        perms = []
        if obj.can_approve_results:
            perms.append('Approve')
        if obj.can_release_reports:
            perms.append('Release')
        if obj.can_manage_users:
            perms.append('Users')
        return ', '.join(perms) if perms else '-'
    get_permission_summary.short_description = 'Key Permissions'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile model."""
    list_display = ('user', 'role', 'department', 'employee_id', 'is_active_lims', 'is_locked')
    list_filter = ('role', 'is_active_lims', 'is_locked', 'department')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'employee_id')
    readonly_fields = ('created_at', 'updated_at', 'last_activity', 'last_password_change')
    raw_id_fields = ('user',)

    fieldsets = (
        (None, {
            'fields': ('user', 'role')
        }),
        ('Professional Info', {
            'fields': ('employee_id', 'department', 'title', 'phone', 'extension')
        }),
        ('Permissions Override', {
            'fields': ('can_approve_results', 'can_release_reports')
        }),
        ('Account Status', {
            'fields': ('is_active_lims', 'is_locked', 'login_attempts', 'require_password_change')
        }),
        ('Qualifications', {
            'fields': ('qualifications', 'signature_image'),
            'classes': ('collapse',)
        }),
        ('Activity', {
            'fields': ('last_activity', 'last_password_change', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['unlock_accounts', 'reset_login_attempts', 'require_password_change']

    def unlock_accounts(self, request, queryset):
        queryset.update(is_locked=False, login_attempts=0)
        self.message_user(request, f"Unlocked {queryset.count()} accounts.")
    unlock_accounts.short_description = "Unlock selected accounts"

    def reset_login_attempts(self, request, queryset):
        queryset.update(login_attempts=0)
        self.message_user(request, f"Reset login attempts for {queryset.count()} accounts.")
    reset_login_attempts.short_description = "Reset login attempts"

    def require_password_change(self, request, queryset):
        queryset.update(require_password_change=True)
        self.message_user(request, f"Password change required for {queryset.count()} accounts.")
    require_password_change.short_description = "Require password change"


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin for UserSession model."""
    list_display = ('user', 'ip_address', 'created_at', 'last_activity', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'ip_address')
    readonly_fields = ('session_key', 'user', 'ip_address', 'user_agent', 'created_at', 'last_activity')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False  # Sessions are created automatically

    actions = ['terminate_sessions']

    def terminate_sessions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Terminated {queryset.count()} sessions.")
    terminate_sessions.short_description = "Terminate selected sessions"
