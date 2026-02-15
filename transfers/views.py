# transfers/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q

from .models import Transfer, TransferItem
from .forms import (
    TransferForm,
    TransferItemFormSet,
    TransferReceiveForm,
    TransferSearchForm,
    QuickTransferForm
)
from .services.tracking import TransferTrackingService


@login_required
def transfer_list(request):
    """Display list of all transfers with filtering."""
    form = TransferSearchForm(request.GET)
    transfers = Transfer.objects.all().order_by('-transfer_date')

    # Apply filters
    if form.is_valid():
        if form.cleaned_data.get('query'):
            query = form.cleaned_data['query']
            transfers = transfers.filter(
                Q(transfer_number__icontains=query) |
                Q(source_location__icontains=query) |
                Q(destination_location__icontains=query) |
                Q(tracking_number__icontains=query)
            )

        if form.cleaned_data.get('status'):
            transfers = transfers.filter(status=form.cleaned_data['status'])

        if form.cleaned_data.get('courier'):
            transfers = transfers.filter(
                courier__icontains=form.cleaned_data['courier']
            )

        if form.cleaned_data.get('date_from'):
            transfers = transfers.filter(
                transfer_date__date__gte=form.cleaned_data['date_from']
            )

        if form.cleaned_data.get('date_to'):
            transfers = transfers.filter(
                transfer_date__date__lte=form.cleaned_data['date_to']
            )

    # Pagination
    paginator = Paginator(transfers, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'form': form,
        'total_count': transfers.count(),
    }
    return render(request, 'transfers/transfer_list.html', context)


@login_required
def transfer_detail(request, transfer_number):
    """Display details of a specific transfer."""
    transfer = get_object_or_404(Transfer, transfer_number=transfer_number)
    items = transfer.items.all()

    context = {
        'transfer': transfer,
        'items': items,
    }
    return render(request, 'transfers/transfer_detail.html', context)


@login_required
def transfer_create(request):
    """Create a new transfer."""
    if request.method == 'POST':
        form = TransferForm(request.POST)
        formset = TransferItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            transfer = form.save(commit=False)
            transfer.initiated_by = request.user
            transfer.save()

            formset.instance = transfer
            formset.save()

            messages.success(
                request,
                f'Transfer {transfer.transfer_number} created successfully.'
            )
            return redirect('transfers:transfer_detail', transfer_number=transfer.transfer_number)
    else:
        form = TransferForm()
        formset = TransferItemFormSet()

    context = {
        'form': form,
        'formset': formset,
        'title': 'Create New Transfer',
    }
    return render(request, 'transfers/transfer_form.html', context)


@login_required
def transfer_edit(request, transfer_number):
    """Edit an existing transfer."""
    transfer = get_object_or_404(Transfer, transfer_number=transfer_number)

    # Only allow editing of pending transfers
    if transfer.status not in ['PENDING']:
        messages.error(
            request,
            'Only pending transfers can be edited.'
        )
        return redirect('transfers:transfer_detail', transfer_number=transfer_number)

    if request.method == 'POST':
        form = TransferForm(request.POST, instance=transfer)
        formset = TransferItemFormSet(request.POST, instance=transfer)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            messages.success(
                request,
                f'Transfer {transfer.transfer_number} updated successfully.'
            )
            return redirect('transfers:transfer_detail', transfer_number=transfer.transfer_number)
    else:
        form = TransferForm(instance=transfer)
        formset = TransferItemFormSet(instance=transfer)

    context = {
        'form': form,
        'formset': formset,
        'transfer': transfer,
        'title': f'Edit Transfer {transfer.transfer_number}',
    }
    return render(request, 'transfers/transfer_form.html', context)


@login_required
def transfer_quick_create(request):
    """Quick transfer creation with multiple samples."""
    if request.method == 'POST':
        form = QuickTransferForm(request.POST)

        if form.is_valid():
            tracking_service = TransferTrackingService()

            # Prepare items from sample IDs
            items = [
                {'sample_id': sid, 'quantity': 1}
                for sid in form.cleaned_data['sample_ids']
            ]

            transfer = tracking_service.create_transfer(
                source_location=form.cleaned_data['source_location'],
                destination_location=form.cleaned_data['destination_location'],
                items=items,
                user=request.user,
                courier=form.cleaned_data.get('courier', ''),
                shipment_conditions=form.cleaned_data['shipment_conditions']
            )

            messages.success(
                request,
                f'Transfer {transfer.transfer_number} created with {len(items)} sample(s).'
            )
            return redirect('transfers:transfer_detail', transfer_number=transfer.transfer_number)
    else:
        form = QuickTransferForm()

    context = {
        'form': form,
        'title': 'Quick Transfer Creation',
    }
    return render(request, 'transfers/transfer_quick_create.html', context)


@login_required
def transfer_dispatch(request, transfer_number):
    """Mark a transfer as dispatched (in transit)."""
    transfer = get_object_or_404(Transfer, transfer_number=transfer_number)

    if transfer.status != 'PENDING':
        messages.error(request, 'Only pending transfers can be dispatched.')
        return redirect('transfers:transfer_detail', transfer_number=transfer_number)

    if request.method == 'POST':
        tracking_service = TransferTrackingService()
        tracking_service.dispatch_transfer(transfer, request.user)

        messages.success(
            request,
            f'Transfer {transfer.transfer_number} has been dispatched.'
        )
        return redirect('transfers:transfer_detail', transfer_number=transfer_number)

    context = {
        'transfer': transfer,
    }
    return render(request, 'transfers/transfer_dispatch_confirm.html', context)


@login_required
def transfer_receive(request, transfer_number):
    """Receive a transfer."""
    transfer = get_object_or_404(Transfer, transfer_number=transfer_number)

    if transfer.status != 'IN_TRANSIT':
        messages.error(request, 'Only in-transit transfers can be received.')
        return redirect('transfers:transfer_detail', transfer_number=transfer_number)

    if request.method == 'POST':
        form = TransferReceiveForm(request.POST)

        if form.is_valid():
            tracking_service = TransferTrackingService()
            tracking_service.receive_transfer(transfer, request.user)

            # Add receipt notes
            if form.cleaned_data.get('notes'):
                transfer.notes = f"{transfer.notes}\nReceipt notes: {form.cleaned_data['notes']}".strip()
                transfer.save()

            messages.success(
                request,
                f'Transfer {transfer.transfer_number} has been received.'
            )
            return redirect('transfers:transfer_detail', transfer_number=transfer_number)
    else:
        form = TransferReceiveForm()

    context = {
        'transfer': transfer,
        'form': form,
        'items': transfer.items.all(),
    }
    return render(request, 'transfers/transfer_receive.html', context)


@login_required
def transfer_cancel(request, transfer_number):
    """Cancel a transfer."""
    transfer = get_object_or_404(Transfer, transfer_number=transfer_number)

    if transfer.status in ['RECEIVED', 'CANCELLED']:
        messages.error(request, 'This transfer cannot be cancelled.')
        return redirect('transfers:transfer_detail', transfer_number=transfer_number)

    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        transfer.cancel(reason)

        messages.success(
            request,
            f'Transfer {transfer.transfer_number} has been cancelled.'
        )
        return redirect('transfers:transfer_detail', transfer_number=transfer_number)

    context = {
        'transfer': transfer,
    }
    return render(request, 'transfers/transfer_cancel_confirm.html', context)


@login_required
def transfer_tracking(request, transfer_number):
    """Get tracking information for a transfer."""
    tracking_service = TransferTrackingService()
    status = tracking_service.get_transfer_status(transfer_number)

    if status is None:
        messages.error(request, 'Transfer not found.')
        return redirect('transfers:transfer_list')

    context = {
        'status': status,
    }
    return render(request, 'transfers/transfer_tracking.html', context)


@login_required
def sample_movement_history(request, sample_id):
    """Display movement history for a specific sample."""
    tracking_service = TransferTrackingService()
    history = tracking_service.get_sample_movement_history(sample_id)

    context = {
        'sample_id': sample_id,
        'history': history,
    }
    return render(request, 'transfers/sample_movement_history.html', context)


@login_required
def active_transfers(request):
    """Display all active (pending/in-transit) transfers."""
    tracking_service = TransferTrackingService()
    transfers = tracking_service.get_active_transfers()

    # Get overdue transfers
    overdue = tracking_service.get_overdue_transfers()

    context = {
        'transfers': transfers,
        'overdue_transfers': overdue,
    }
    return render(request, 'transfers/active_transfers.html', context)


@login_required
def transfer_statistics(request):
    """Display transfer statistics dashboard."""
    tracking_service = TransferTrackingService()
    stats = tracking_service.get_transfer_statistics()

    context = {
        'statistics': stats,
    }
    return render(request, 'transfers/transfer_statistics.html', context)


# API Views

@login_required
@require_http_methods(["GET"])
def api_transfer_status(request, transfer_number):
    """API endpoint for transfer status."""
    tracking_service = TransferTrackingService()
    status = tracking_service.get_transfer_status(transfer_number)

    if status is None:
        return JsonResponse({'error': 'Transfer not found'}, status=404)

    # Convert datetime objects to ISO format for JSON serialization
    for key in ['transfer_date', 'expected_arrival_date', 'actual_arrival_date']:
        if status.get(key):
            status[key] = status[key].isoformat()

    return JsonResponse(status)


@login_required
@require_http_methods(["GET"])
def api_sample_history(request, sample_id):
    """API endpoint for sample movement history."""
    tracking_service = TransferTrackingService()
    history = tracking_service.get_sample_movement_history(sample_id)

    # Convert datetime objects to ISO format
    for record in history:
        for key in ['transfer_date', 'received_at']:
            if record.get(key):
                record[key] = record[key].isoformat()

    return JsonResponse({'sample_id': sample_id, 'history': history})


@login_required
@require_http_methods(["POST"])
def api_report_discrepancy(request, transfer_number, sample_id):
    """API endpoint for reporting discrepancies."""
    description = request.POST.get('description', '')

    if not description:
        return JsonResponse({'error': 'Description is required'}, status=400)

    tracking_service = TransferTrackingService()
    success = tracking_service.report_discrepancy(
        transfer_number,
        sample_id,
        description,
        request.user
    )

    if success:
        return JsonResponse({'success': True, 'message': 'Discrepancy reported'})
    else:
        return JsonResponse({'error': 'Transfer or sample not found'}, status=404)
