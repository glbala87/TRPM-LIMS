# messaging/views.py

from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q

from .models import MessageThread, Message, Notification


class InboxView(LoginRequiredMixin, ListView):
    model = MessageThread
    template_name = 'messaging/inbox.html'
    context_object_name = 'threads'
    paginate_by = 25

    def get_queryset(self):
        return MessageThread.objects.filter(
            participants=self.request.user
        ).order_by('-updated_at')


class ThreadDetailView(LoginRequiredMixin, DetailView):
    model = MessageThread
    template_name = 'messaging/thread_detail.html'
    context_object_name = 'thread'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages_list'] = self.object.messages.all().order_by('created_at')
        return context


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'messaging/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 50

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).order_by('-created_at')
