# projects/views.py

from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import (
    ProjectCategory, Project, ProjectMember,
    ProjectSample, ProjectMilestone, ProjectDocument
)


class ProjectCategoryListView(LoginRequiredMixin, ListView):
    model = ProjectCategory
    template_name = 'projects/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return ProjectCategory.objects.filter(is_active=True)


class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 25

    def get_queryset(self):
        queryset = Project.objects.select_related(
            'category', 'principal_investigator'
        )

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)

        return queryset.order_by('-created_at')


class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['members'] = self.object.members.select_related('user').filter(is_active=True)
        context['recent_samples'] = self.object.samples.select_related('molecular_sample')[:10]
        context['milestones'] = self.object.milestones.order_by('order', 'target_date')
        context['documents'] = self.object.documents.order_by('-uploaded_at')[:5]
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = [
        'name', 'short_name', 'description', 'category',
        'start_date', 'end_date', 'principal_investigator',
        'ethics_approval_number', 'ethics_approval_date', 'ethics_expiry_date',
        'consent_required', 'funding_source', 'grant_number', 'budget',
        'target_sample_count', 'target_participant_count', 'notes'
    ]
    success_url = reverse_lazy('projects:project_list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'projects/project_form.html'
    fields = [
        'name', 'short_name', 'description', 'category', 'status',
        'start_date', 'end_date', 'principal_investigator',
        'ethics_approval_number', 'ethics_approval_date', 'ethics_expiry_date',
        'ethics_document', 'consent_required', 'consent_form',
        'funding_source', 'grant_number', 'budget',
        'target_sample_count', 'target_participant_count', 'notes'
    ]

    def get_success_url(self):
        return reverse_lazy('projects:project_detail', kwargs={'pk': self.object.pk})


class ProjectMemberListView(LoginRequiredMixin, ListView):
    model = ProjectMember
    template_name = 'projects/member_list.html'
    context_object_name = 'members'

    def get_queryset(self):
        project_id = self.kwargs.get('pk')
        return ProjectMember.objects.filter(
            project_id=project_id, is_active=True
        ).select_related('user')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('pk'))
        return context


class ProjectMemberCreateView(LoginRequiredMixin, CreateView):
    model = ProjectMember
    template_name = 'projects/member_form.html'
    fields = ['user', 'role', 'can_add_samples', 'can_edit_samples', 'can_view_results', 'can_manage_members']

    def form_valid(self, form):
        form.instance.project_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:member_list', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('pk'))
        return context


class ProjectSampleListView(LoginRequiredMixin, ListView):
    model = ProjectSample
    template_name = 'projects/sample_list.html'
    context_object_name = 'samples'
    paginate_by = 50

    def get_queryset(self):
        project_id = self.kwargs.get('pk')
        return ProjectSample.objects.filter(
            project_id=project_id
        ).select_related('molecular_sample')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('pk'))
        return context


class ProjectSampleCreateView(LoginRequiredMixin, CreateView):
    model = ProjectSample
    template_name = 'projects/sample_form.html'
    fields = [
        'molecular_sample', 'external_sample_id', 'subject_id',
        'consent_obtained', 'consent_date', 'consent_version', 'notes'
    ]

    def form_valid(self, form):
        form.instance.project_id = self.kwargs['pk']
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:sample_list', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('pk'))
        return context


class ProjectMilestoneListView(LoginRequiredMixin, ListView):
    model = ProjectMilestone
    template_name = 'projects/milestone_list.html'
    context_object_name = 'milestones'

    def get_queryset(self):
        project_id = self.kwargs.get('pk')
        return ProjectMilestone.objects.filter(project_id=project_id).order_by('order', 'target_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('pk'))
        return context


class ProjectMilestoneCreateView(LoginRequiredMixin, CreateView):
    model = ProjectMilestone
    template_name = 'projects/milestone_form.html'
    fields = ['name', 'description', 'target_date', 'status', 'order']

    def form_valid(self, form):
        form.instance.project_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:milestone_list', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('pk'))
        return context


class ProjectDocumentListView(LoginRequiredMixin, ListView):
    model = ProjectDocument
    template_name = 'projects/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        project_id = self.kwargs.get('pk')
        return ProjectDocument.objects.filter(project_id=project_id).order_by('-uploaded_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('pk'))
        return context


class ProjectDocumentCreateView(LoginRequiredMixin, CreateView):
    model = ProjectDocument
    template_name = 'projects/document_form.html'
    fields = ['title', 'document_type', 'file', 'version', 'description']

    def form_valid(self, form):
        form.instance.project_id = self.kwargs['pk']
        form.instance.uploaded_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('projects:document_list', kwargs={'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = get_object_or_404(Project, pk=self.kwargs.get('pk'))
        return context
