from django.urls import path
from . import views

urlpatterns = [
    path('reagents/', views.reagent_list, name='reagent_list'),
    # You can add other URLs here for adding, editing, or viewing specific reagents
]
