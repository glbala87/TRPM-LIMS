# molecular_diagnostics/views/sample_views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from ..models import MolecularSample
from ..services.workflow_engine import WorkflowEngine


@login_required
def sample_list(request):
    """List all molecular samples with filtering"""
    samples = MolecularSample.objects.select_related(
        'lab_order__patient',
        'sample_type',
        'test_panel'
    ).order_by('-received_datetime')

    # Apply filters
    status = request.GET.get('status')
    if status:
        samples = samples.filter(workflow_status=status)

    priority = request.GET.get('priority')
    if priority:
        samples = samples.filter(priority=priority)

    context = {
        'samples': samples,
        'status_choices': MolecularSample.WORKFLOW_STATUS_CHOICES,
    }

    return render(request, 'molecular_diagnostics/sample_list.html', context)


@login_required
def sample_detail(request, pk):
    """Detailed view of a molecular sample"""
    sample = get_object_or_404(
        MolecularSample.objects.select_related(
            'lab_order__patient',
            'sample_type',
            'test_panel',
            'current_step',
            'storage_location'
        ),
        pk=pk
    )

    # Get sample history
    history = sample.history.select_related('user', 'from_step', 'to_step').order_by('-timestamp')

    # Get available transitions
    workflow_engine = WorkflowEngine()
    available_transitions = workflow_engine.get_available_transitions(sample)

    # Get results if any
    results = sample.results.all()

    context = {
        'sample': sample,
        'history': history,
        'available_transitions': available_transitions,
        'results': results,
    }

    return render(request, 'molecular_diagnostics/sample_detail.html', context)


@login_required
def sample_transition(request, pk):
    """Handle sample workflow transition"""
    sample = get_object_or_404(MolecularSample, pk=pk)

    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        notes = request.POST.get('notes', '')

        workflow_engine = WorkflowEngine()

        try:
            workflow_engine.transition(
                sample=sample,
                new_status=new_status,
                user=request.user,
                notes=notes
            )
            messages.success(request, f'Sample transitioned to {new_status}')
        except ValueError as e:
            messages.error(request, str(e))

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'new_status': sample.workflow_status
            })

        return redirect('molecular_diagnostics:sample_detail', pk=pk)

    return redirect('molecular_diagnostics:sample_detail', pk=pk)
