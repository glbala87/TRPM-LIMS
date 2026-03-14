# qms/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q

from .models import Document, DocumentVersion, DocumentFolder, DocumentCategory, DocumentReviewCycle


class DocumentListView(LoginRequiredMixin, ListView):
    model = Document
    template_name = 'qms/document_list.html'
    context_object_name = 'documents'
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get('q')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(document_number__icontains=search)
            )
        category = self.request.GET.get('category')
        if category:
            qs = qs.filter(category_id=category)
        return qs.order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = DocumentCategory.objects.all()
        return context


class DocumentDetailView(LoginRequiredMixin, DetailView):
    model = Document
    template_name = 'qms/document_detail.html'
    context_object_name = 'document'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['versions'] = DocumentVersion.objects.filter(document=self.object).order_by('-version_number')
        context['review_cycles'] = DocumentReviewCycle.objects.filter(document=self.object).order_by('-created_at')
        return context


class FolderListView(LoginRequiredMixin, ListView):
    model = DocumentFolder
    template_name = 'qms/folder_list.html'
    context_object_name = 'folders'

    def get_queryset(self):
        return super().get_queryset().filter(parent=None).order_by('name')


class FolderDetailView(LoginRequiredMixin, DetailView):
    model = DocumentFolder
    template_name = 'qms/folder_detail.html'
    context_object_name = 'folder'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subfolders'] = DocumentFolder.objects.filter(parent=self.object)
        context['documents'] = Document.objects.filter(folder=self.object)
        return context
