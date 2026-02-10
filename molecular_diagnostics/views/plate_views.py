# molecular_diagnostics/views/plate_views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from ..models import PCRPlate, PlateWell


@login_required
def plate_list(request):
    """List all PCR plates"""
    plates = PCRPlate.objects.select_related(
        'instrument_run__instrument',
        'created_by'
    ).prefetch_related('wells').order_by('-created_at')

    context = {
        'plates': plates,
    }

    return render(request, 'molecular_diagnostics/plate_list.html', context)


@login_required
def plate_detail(request, pk):
    """Detailed view of a PCR plate"""
    plate = get_object_or_404(
        PCRPlate.objects.select_related(
            'instrument_run__instrument'
        ).prefetch_related(
            'wells__sample',
            'wells__control_sample'
        ),
        pk=pk
    )

    context = {
        'plate': plate,
        'layout': plate.get_layout(),
    }

    return render(request, 'molecular_diagnostics/plate_detail.html', context)


@login_required
def plate_layout(request, pk):
    """API endpoint for plate layout data"""
    plate = get_object_or_404(PCRPlate, pk=pk)

    # Build layout data
    layout = {}
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    if plate.plate_type == '384':
        rows = [chr(i) for i in range(ord('A'), ord('P') + 1)]

    cols = range(1, 13) if plate.plate_type == '96' else range(1, 25)

    wells = plate.wells.select_related('sample', 'control_sample')
    well_dict = {w.position: w for w in wells}

    for row in rows:
        for col in cols:
            position = f"{row}{col}"
            well = well_dict.get(position)

            if well:
                layout[position] = {
                    'id': well.id,
                    'sample_id': well.sample.sample_id if well.sample else None,
                    'control_type': well.control_type,
                    'is_control': well.is_control,
                }
            else:
                layout[position] = {
                    'id': None,
                    'sample_id': None,
                    'control_type': 'EMPTY',
                    'is_control': False,
                }

    return JsonResponse({
        'plate_id': plate.id,
        'barcode': plate.barcode,
        'plate_type': plate.plate_type,
        'rows': rows,
        'columns': list(cols),
        'layout': layout,
    })
