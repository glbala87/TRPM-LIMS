# qms/urls.py

from django.urls import path
from . import views

app_name = 'qms'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('document/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),
    path('folders/', views.FolderListView.as_view(), name='folder_list'),
    path('folders/<int:pk>/', views.FolderDetailView.as_view(), name='folder_detail'),
]
