from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # REST API
    path('api/', include('api.urls')),

    # Core LIMS apps
    path('', include('lab_management.urls')),
    path('reagents/', include('reagents.urls')),
    path('molecular/', include('molecular_diagnostics.urls')),
    path('equipment/', include('equipment.urls')),
    path('storage/', include('storage.urls')),

    # Phase 1 apps
    path('audit/', include('audit.urls')),
    path('data/', include('data_exchange.urls')),

    # Phase 2 apps
    path('analytics/', include('analytics.urls')),
    path('transfers/', include('transfers.urls')),
    path('compliance/', include('compliance.urls')),

    # Phase 3 apps
    path('instruments/', include('instruments.urls')),

    # Phase 4 apps - Feature gaps implementation
    path('tenants/', include('tenants.urls')),
    path('single-cell/', include('single_cell.urls')),
    path('bioinformatics/', include('bioinformatics.urls')),
    path('ontology/', include('ontology.urls')),
    path('sensors/', include('sensors.urls')),
    path('custom-fields/', include('dynamic_fields.urls')),
    path('projects/', include('projects.urls')),
    path('billing/', include('billing.urls')),

    # Phase 5 apps - Additional features
    path('microbiology/', include('microbiology.urls')),
    path('qms/', include('qms.urls')),
    path('messaging/', include('messaging.urls')),
    path('pathology/', include('pathology.urls')),

    # Phase 6 apps - Molecular/Genomics Enhancements
    path('pgx/', include('pharmacogenomics.urls')),
]

# Serve media files in development (only when DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
