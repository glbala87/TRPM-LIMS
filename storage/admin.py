# storage/admin.py

from django.contrib import admin
from django.utils.html import format_html
from .models import StorageUnit, StorageRack, StoragePosition, StorageLog


class StorageRackInline(admin.TabularInline):
    model = StorageRack
    extra = 0
    fields = ['rack_id', 'name', 'shelf_number', 'rows', 'columns', 'is_active']
    ordering = ['shelf_number', 'rack_id']


class StoragePositionInline(admin.TabularInline):
    model = StoragePosition
    extra = 0
    fields = ['position', 'is_occupied', 'is_reserved', 'stored_at']
    readonly_fields = ['stored_at']
    ordering = ['position']
    max_num = 20


@admin.register(StorageUnit)
class StorageUnitAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'unit_type', 'temperature_display',
        'status_display', 'capacity_display', 'location'
    ]
    list_filter = ['unit_type', 'status', 'is_active']
    search_fields = ['name', 'code', 'location']
    inlines = [StorageRackInline]

    fieldsets = (
        ('Unit Information', {
            'fields': ('name', 'code', 'unit_type', 'location')
        }),
        ('Temperature', {
            'fields': (
                ('temperature_min', 'temperature_max', 'temperature_target'),
            )
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Equipment Details', {
            'fields': ('manufacturer', 'model', 'serial_number'),
            'classes': ('collapse',)
        }),
        ('Features', {
            'fields': ('capacity_description', 'has_temperature_monitoring', 'has_alarm')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )

    def temperature_display(self, obj):
        if obj.temperature_target is not None:
            return f"{obj.temperature_target}°C"
        return obj.temperature_range or "-"
    temperature_display.short_description = 'Temp'

    def status_display(self, obj):
        colors = {
            'ACTIVE': '#38a169',
            'MAINTENANCE': '#d69e2e',
            'FULL': '#805ad5',
            'OUT_OF_SERVICE': '#c53030',
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'

    def capacity_display(self, obj):
        total = obj.total_positions
        occupied = obj.occupied_positions
        if total > 0:
            pct = (occupied / total) * 100
            color = '#38a169' if pct < 75 else '#d69e2e' if pct < 90 else '#c53030'
            return format_html(
                '<span style="color: {};">{}/{} ({:.0f}%)</span>',
                color, occupied, total, pct
            )
        return "0/0"
    capacity_display.short_description = 'Capacity'


@admin.register(StorageRack)
class StorageRackAdmin(admin.ModelAdmin):
    list_display = [
        'rack_id', 'unit', 'shelf_number', 'dimensions',
        'capacity_display', 'is_active'
    ]
    list_filter = ['unit', 'is_active']
    search_fields = ['rack_id', 'name', 'unit__name']
    inlines = [StoragePositionInline]

    fieldsets = (
        ('Rack Information', {
            'fields': ('unit', 'rack_id', 'name', 'shelf_number')
        }),
        ('Dimensions', {
            'fields': ('rows', 'columns', 'rack_type')
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
    )

    def dimensions(self, obj):
        return f"{obj.rows}×{obj.columns}"
    dimensions.short_description = 'Size'

    def capacity_display(self, obj):
        return f"{obj.occupied_positions}/{obj.total_positions}"
    capacity_display.short_description = 'Used'


@admin.register(StoragePosition)
class StoragePositionAdmin(admin.ModelAdmin):
    list_display = [
        'full_location', 'position', 'is_occupied',
        'is_reserved', 'stored_at', 'stored_by'
    ]
    list_filter = ['is_occupied', 'is_reserved', 'rack__unit']
    search_fields = ['position', 'rack__rack_id', 'rack__unit__name']
    readonly_fields = ['stored_at']

    fieldsets = (
        ('Location', {
            'fields': ('rack', 'position', 'row', 'column')
        }),
        ('Status', {
            'fields': ('is_occupied', 'is_reserved')
        }),
        ('Storage Info', {
            'fields': ('stored_at', 'stored_by', 'notes')
        }),
    )


@admin.register(StorageLog)
class StorageLogAdmin(admin.ModelAdmin):
    list_display = [
        'sample_id', 'action', 'location_display',
        'timestamp', 'performed_by'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = ['sample_id', 'position__rack__unit__name']
    readonly_fields = [
        'position', 'sample_id', 'action', 'from_position',
        'to_position', 'timestamp', 'performed_by'
    ]
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def location_display(self, obj):
        if obj.action == 'MOVE':
            return f"{obj.from_position} → {obj.to_position}"
        return obj.to_position or obj.from_position or "-"
    location_display.short_description = 'Location'
