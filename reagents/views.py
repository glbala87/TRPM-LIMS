# reagents/views.py
from django.shortcuts import render
from .models import Reagent

def reagent_list(request):
    # Fetch all reagents from the database
    reagents = Reagent.objects.all()
    # Render the reagents in the HTML template
    return render(request, 'reagents/reagent_list.html', {'reagents': reagents})
