from django.shortcuts import render, get_object_or_404, redirect
from .forms import PatientForm, LabOrderForm, TestResultForm
from .models import Patient
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render
from .models import LabOrder

# Patient List View
def patient_list(request):
    # Default queryset to fetch all patients
    patients = Patient.objects.all()

    # If there is a search query, filter the patients by OP NO
    if 'op_no' in request.GET:
        op_no = request.GET['op_no']
        patients = patients.filter(OP_NO__icontains=op_no)  # Case-insensitive search

    return render(request, 'lab_management/patient_list.html', {'patients': patients})


# Patient Registration
def patient_registration(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('patient_list')
    else:
        form = PatientForm()
    return render(request, 'lab_management/patient_registration.html', {'form': form})

# Lab Order
def lab_orders(request):
    if request.method == 'POST':
        form = LabOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lab_orders')
    else:
        form = LabOrderForm()
    lab_orders = LabOrder.objects.all()
    return render(request, 'lab_management/lab_orders.html', {'form': form, 'lab_orders': lab_orders})


# Define the lab_order_view function
def lab_order_view(request):
    test_categories = dict(TEST_CATEGORIES)  # Convert to a dictionary if necessary
    test_choices = TEST_CHOICES
    
    # Render the form template and pass the necessary context
    return render(request, 'lab_managment/lab_order_form.html', {
        'test_categories': test_categories,
        'test_choices': test_choices,
    })


# Results Entry/View
def results_entry_view(request):
    if request.method == 'POST':
        form = TestResultForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('results_entry_view')
    else:
        form = TestResultForm()
    test_results = TestResult.objects.all()
    return render(request, 'lab_management/results_entry_view.html', {'form': form, 'test_results': test_results})

# Autocomplete view for patient OP_NO search
def patient_autocomplete(request):
    if 'term' in request.GET:
        term = request.GET['term']
        # Search patients by OP_NO, first name or last name
        patients = Patient.objects.filter(
            Q(OP_NO__icontains=term) | Q(first_name__icontains=term) | Q(last_name__icontains=term)
        )[:10]  # Limit results to 10 for performance
        results = []
        for patient in patients:
            results.append({
                'id': patient.id,
                'label': f"{patient.OP_NO} - {patient.first_name} {patient.last_name}",
                'value': patient.OP_NO
            })
        return JsonResponse(results, safe=False)
    return JsonResponse([], safe=False)
