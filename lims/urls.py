from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin page for the Django admin interface
    path('', include('lab_management.urls')),  # Main app URL (lab_management)
    path('reagents/', include('reagents.urls')),  # Reagents app URL
    path('molecular/', include('molecular_diagnostics.urls')),  # Molecular diagnostics app
    path('equipment/', include('equipment.urls')),  # Equipment management app
    path('storage/', include('storage.urls')),  # Storage tracking app
]

# Serve media files in development (only when DEBUG=True)
if settings.DEBUG:
    # This line ensures that the media files (like barcode images) are served correctly during development.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
