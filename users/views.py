# users/views.py

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.db.models import Q
from django import forms

from .models import Role, UserProfile


# --- Forms ---

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    role = forms.ModelChoiceField(queryset=Role.objects.filter(is_active=True), required=False)
    department = forms.CharField(max_length=100, required=False)
    employee_id = forms.CharField(max_length=50, required=False)
    title = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data.get('role')
            profile.department = self.cleaned_data.get('department', '')
            profile.employee_id = self.cleaned_data.get('employee_id', '')
            profile.title = self.cleaned_data.get('title', '')
            profile.phone = self.cleaned_data.get('phone', '')
            profile.save()
        return user


class UserUpdateForm(forms.ModelForm):
    role = forms.ModelChoiceField(queryset=Role.objects.filter(is_active=True), required=False)
    department = forms.CharField(max_length=100, required=False)
    employee_id = forms.CharField(max_length=50, required=False)
    title = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'userprofile'):
            profile = self.instance.userprofile
            self.fields['role'].initial = profile.role
            self.fields['department'].initial = profile.department
            self.fields['employee_id'].initial = profile.employee_id
            self.fields['title'].initial = profile.title
            self.fields['phone'].initial = profile.phone

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data.get('role')
            profile.department = self.cleaned_data.get('department', '')
            profile.employee_id = self.cleaned_data.get('employee_id', '')
            profile.title = self.cleaned_data.get('title', '')
            profile.phone = self.cleaned_data.get('phone', '')
            profile.save()
        return user


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['department', 'title', 'phone', 'extension', 'qualifications']
        widgets = {
            'qualifications': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if commit:
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
        return profile


# --- Auth Views ---

class LIMSLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class LIMSLogoutView(LogoutView):
    template_name = 'users/logout.html'


# --- Profile Views ---

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        context['profile'] = profile
        context['recent_activities'] = []
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = ProfileEditForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)


# --- User Management Views (Admin) ---

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class UserListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = User
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 25

    def get_queryset(self):
        qs = User.objects.select_related('userprofile', 'userprofile__role').all()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(
                Q(username__icontains=q) | Q(first_name__icontains=q) |
                Q(last_name__icontains=q) | Q(email__icontains=q)
            )
        role = self.request.GET.get('role')
        if role:
            qs = qs.filter(userprofile__role_id=role)
        department = self.request.GET.get('department')
        if department:
            qs = qs.filter(userprofile__department=department)
        status = self.request.GET.get('status')
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)

        sort = self.request.GET.get('sort', 'name')
        order = self.request.GET.get('order', 'asc')
        if sort == 'last_login':
            qs = qs.order_by(f'{"-" if order == "desc" else ""}last_login')
        else:
            qs = qs.order_by(f'{"-" if order == "desc" else ""}first_name', 'last_name')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = Role.objects.filter(is_active=True)
        context['departments'] = UserProfile.objects.exclude(
            department=''
        ).values_list('department', flat=True).distinct()
        context['total_count'] = User.objects.count()
        return context


class UserDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = User
    template_name = 'users/user_detail.html'
    context_object_name = 'user_obj'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, _ = UserProfile.objects.get_or_create(user=self.object)
        context['profile'] = profile
        return context


class UserCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = 'Add User'
        return context

    def form_valid(self, form):
        messages.success(self.request, f'User {form.cleaned_data["username"]} created successfully.')
        return super().form_valid(form)


class UserEditView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:user_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_title'] = f'Edit User: {self.object.get_full_name() or self.object.username}'
        return context

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = User
    success_url = reverse_lazy('users:user_list')

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            messages.error(request, 'You cannot delete your own account.')
            return redirect('users:user_list')
        messages.success(request, f'User {user.username} deleted.')
        return super().post(request, *args, **kwargs)


# --- Role Views ---

class RoleListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Role
    template_name = 'users/role_list.html'
    context_object_name = 'roles'


class RoleDetailView(LoginRequiredMixin, StaffRequiredMixin, DetailView):
    model = Role
    template_name = 'users/role_detail.html'
    context_object_name = 'role'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users_with_role'] = UserProfile.objects.filter(
            role=self.object
        ).select_related('user')
        return context
