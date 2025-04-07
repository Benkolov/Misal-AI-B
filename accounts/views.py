from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserUpdateForm
from django.contrib.auth.mixins import LoginRequiredMixin



class RegisterView(CreateView):
    template_name = "user/register.html"
    form_class = CustomUserCreationForm

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        user = self.object

        if user:
            if not user.username:
                user.username = user.email.split('@')[0]
                user.save()

            login(request, user)

        return response

    def get_success_url(self):
        return reverse("profile", kwargs={"pk": self.object.pk})



class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "user/profile.html"

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserUpdateForm
    template_name = "user/profile_edit.html"

    def get_success_url(self):
        return reverse("profile", kwargs={"pk": self.request.user.pk})

    def get_object(self, queryset=None):
        return self.request.user


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    model = CustomUser
    template_name = "user/profile_confirm_delete.html"
    success_url = reverse_lazy("post list")

    def get_object(self, queryset=None):
        return self.request.user
