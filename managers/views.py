from django.urls import reverse_lazy
from django.views.generic import TemplateView

from managers.mixins import LoginRequiredMixin
from users.models import CustomUser
from users.views import BaseUserLoginView


class LoginView(BaseUserLoginView):
    success_url = reverse_lazy('manager_dashboard')
    user_type = CustomUser.Type.MANAGER


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'managers/dashboard.html'
