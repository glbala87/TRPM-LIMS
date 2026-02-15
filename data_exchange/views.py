# data_exchange/views.py

"""
Views for the Data Exchange app.

Provides views for importing and exporting data.
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.utils import timezone
from django.core.paginator import Paginator

from .models import ImportJob, ImportedRecord, ExportTemplate, ExportJob


class ImportListView(LoginRequiredMixin, ListView):
    """List view for import jobs."""

    model = ImportJob
    template_name = 'data_exchange/import_list.html'
    context_object_name = 'imports'
    paginate_by = 25

    def get_queryset(self):
        """Filter and order import jobs."""
        queryset = ImportJob.objects.select_related('created_by').order_by('-created_at')

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Filter by import type
        import_type = self.request.GET.get('import_type')
        if import_type:
            queryset = queryset.filter(import_type=import_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = ImportJob.STATUS_CHOICES
        context['type_choices'] = ImportJob.IMPORT_TYPE_CHOICES
        return context


class ImportCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create view for starting a new import."""

    model = ImportJob
    template_name = 'data_exchange/import_create.html'
    fields = ['import_type', 'file', 'notes']
    permission_required = 'data_exchange.add_importjob'

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'PENDING'
        messages.success(self.request, 'Import job created. Please review and confirm.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('data_exchange:import_preview', kwargs={'pk': self.object.pk})


class ImportDetailView(LoginRequiredMixin, DetailView):
    """Detail view for an import job."""

    model = ImportJob
    template_name = 'data_exchange/import_detail.html'
    context_object_name = 'import_job'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get imported records with pagination
        records = self.object.records.all().order_by('-created_at')
        paginator = Paginator(records, 50)
        page = self.request.GET.get('page')
        context['records'] = paginator.get_page(page)

        # Statistics
        context['stats'] = {
            'total': records.count(),
            'success': records.filter(status='SUCCESS').count(),
            'error': records.filter(status='ERROR').count(),
            'skipped': records.filter(status='SKIPPED').count(),
        }

        return context


def import_preview(request, pk):
    """Preview import data before confirming."""
    import_job = get_object_or_404(ImportJob, pk=pk)

    if import_job.status not in ['PENDING', 'VALIDATED']:
        messages.error(request, 'This import cannot be previewed.')
        return redirect('data_exchange:import_detail', pk=pk)

    # Parse the file and get preview data
    preview_data = []
    errors = []

    try:
        # Get the appropriate importer
        from .importers import get_importer
        importer = get_importer(import_job.import_type)

        if import_job.file:
            # Read first 10 rows for preview
            preview_data, errors = importer.preview(import_job.file, limit=10)

            if not errors:
                import_job.status = 'VALIDATED'
                import_job.save()

    except Exception as e:
        errors.append(str(e))

    context = {
        'import_job': import_job,
        'preview_data': preview_data,
        'errors': errors,
        'headers': preview_data[0].keys() if preview_data else [],
    }

    return render(request, 'data_exchange/import_preview.html', context)


def import_confirm(request, pk):
    """Confirm and process import."""
    import_job = get_object_or_404(ImportJob, pk=pk)

    if request.method != 'POST':
        return redirect('data_exchange:import_preview', pk=pk)

    if import_job.status not in ['PENDING', 'VALIDATED']:
        messages.error(request, 'This import cannot be processed.')
        return redirect('data_exchange:import_detail', pk=pk)

    try:
        # Process the import
        from .importers import get_importer
        importer = get_importer(import_job.import_type)

        import_job.status = 'PROCESSING'
        import_job.started_at = timezone.now()
        import_job.save()

        # Run import
        result = importer.process(import_job)

        import_job.status = 'COMPLETED' if result.get('success') else 'FAILED'
        import_job.completed_at = timezone.now()
        import_job.total_records = result.get('total', 0)
        import_job.success_count = result.get('success_count', 0)
        import_job.error_count = result.get('error_count', 0)
        import_job.save()

        messages.success(
            request,
            f'Import completed: {import_job.success_count} records imported, '
            f'{import_job.error_count} errors.'
        )

    except Exception as e:
        import_job.status = 'FAILED'
        import_job.error_message = str(e)
        import_job.save()
        messages.error(request, f'Import failed: {str(e)}')

    return redirect('data_exchange:import_detail', pk=pk)


def import_cancel(request, pk):
    """Cancel an import job."""
    import_job = get_object_or_404(ImportJob, pk=pk)

    if import_job.status in ['PENDING', 'VALIDATED']:
        import_job.status = 'CANCELLED'
        import_job.save()
        messages.success(request, 'Import cancelled.')
    else:
        messages.error(request, 'This import cannot be cancelled.')

    return redirect('data_exchange:import_list')


class ExportListView(LoginRequiredMixin, ListView):
    """List view for export jobs."""

    model = ExportJob
    template_name = 'data_exchange/export_list.html'
    context_object_name = 'exports'
    paginate_by = 25

    def get_queryset(self):
        return ExportJob.objects.select_related(
            'created_by', 'template'
        ).order_by('-created_at')


class ExportCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create a new export."""

    model = ExportJob
    template_name = 'data_exchange/export_create.html'
    fields = ['template', 'output_format', 'filters']
    permission_required = 'data_exchange.add_exportjob'
    success_url = reverse_lazy('data_exchange:export_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['templates'] = ExportTemplate.objects.filter(is_active=True)
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.status = 'PENDING'

        # Process export
        response = super().form_valid(form)

        # Run export in background (for now, synchronous)
        try:
            from .exporters import run_export
            run_export(self.object)
            messages.success(self.request, 'Export completed successfully.')
        except Exception as e:
            messages.error(self.request, f'Export failed: {str(e)}')

        return response


class ExportDetailView(LoginRequiredMixin, DetailView):
    """Detail view for an export job."""

    model = ExportJob
    template_name = 'data_exchange/export_detail.html'
    context_object_name = 'export_job'


def export_download(request, pk):
    """Download export file."""
    export_job = get_object_or_404(ExportJob, pk=pk)

    if not export_job.output_file:
        messages.error(request, 'Export file not available.')
        return redirect('data_exchange:export_detail', pk=pk)

    response = FileResponse(
        export_job.output_file,
        as_attachment=True,
        filename=export_job.output_file.name.split('/')[-1]
    )
    return response


class ExportTemplateListView(LoginRequiredMixin, ListView):
    """List view for export templates."""

    model = ExportTemplate
    template_name = 'data_exchange/export_template_list.html'
    context_object_name = 'templates'


class ExportTemplateCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create a new export template."""

    model = ExportTemplate
    template_name = 'data_exchange/export_template_form.html'
    fields = ['name', 'description', 'model_name', 'fields', 'filters', 'is_active']
    permission_required = 'data_exchange.add_exporttemplate'
    success_url = reverse_lazy('data_exchange:export_template_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Export template created.')
        return super().form_valid(form)


class ExportTemplateUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update an export template."""

    model = ExportTemplate
    template_name = 'data_exchange/export_template_form.html'
    fields = ['name', 'description', 'model_name', 'fields', 'filters', 'is_active']
    permission_required = 'data_exchange.change_exporttemplate'
    success_url = reverse_lazy('data_exchange:export_template_list')

    def form_valid(self, form):
        messages.success(self.request, 'Export template updated.')
        return super().form_valid(form)


def export_template_run(request, pk):
    """Run an export using a template."""
    template = get_object_or_404(ExportTemplate, pk=pk)

    # Create export job from template
    export_job = ExportJob.objects.create(
        template=template,
        created_by=request.user,
        output_format=request.GET.get('format', 'CSV'),
        status='PENDING',
    )

    try:
        from .exporters import run_export
        run_export(export_job)
        return redirect('data_exchange:export_download', pk=export_job.pk)
    except Exception as e:
        messages.error(request, f'Export failed: {str(e)}')
        return redirect('data_exchange:export_template_list')


def api_validate_import(request):
    """API endpoint to validate import file."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    file = request.FILES.get('file')
    import_type = request.POST.get('import_type')

    if not file or not import_type:
        return JsonResponse({'error': 'File and import_type required'}, status=400)

    try:
        from .importers import get_importer
        importer = get_importer(import_type)
        preview_data, errors = importer.preview(file, limit=5)

        return JsonResponse({
            'valid': len(errors) == 0,
            'preview': preview_data,
            'errors': errors,
            'row_count': len(preview_data),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_export_preview(request):
    """API endpoint to preview export data."""
    template_id = request.GET.get('template_id')

    if not template_id:
        return JsonResponse({'error': 'template_id required'}, status=400)

    template = get_object_or_404(ExportTemplate, pk=template_id)

    try:
        from .exporters import preview_export
        preview = preview_export(template, limit=10)

        return JsonResponse({
            'preview': preview,
            'row_count': len(preview),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
