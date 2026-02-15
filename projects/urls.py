# projects/urls.py

from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # Project Categories
    path('categories/', views.ProjectCategoryListView.as_view(), name='category_list'),

    # Projects
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='project_update'),

    # Project Members
    path('<int:pk>/members/', views.ProjectMemberListView.as_view(), name='member_list'),
    path('<int:pk>/members/add/', views.ProjectMemberCreateView.as_view(), name='member_add'),

    # Project Samples
    path('<int:pk>/samples/', views.ProjectSampleListView.as_view(), name='sample_list'),
    path('<int:pk>/samples/add/', views.ProjectSampleCreateView.as_view(), name='sample_add'),

    # Milestones
    path('<int:pk>/milestones/', views.ProjectMilestoneListView.as_view(), name='milestone_list'),
    path('<int:pk>/milestones/add/', views.ProjectMilestoneCreateView.as_view(), name='milestone_add'),

    # Documents
    path('<int:pk>/documents/', views.ProjectDocumentListView.as_view(), name='document_list'),
    path('<int:pk>/documents/upload/', views.ProjectDocumentCreateView.as_view(), name='document_upload'),
]
