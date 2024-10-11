from django.urls import reverse_lazy
from django.views.generic import TemplateView

from operators.mixins import LoginRequiredMixin
from users.models import CustomUser
from users.views import BaseUserLoginView


class LoginView(BaseUserLoginView):
    success_url = reverse_lazy('operator_dashboard')
    user_type = CustomUser.Type.OPERATOR


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'operators/dashboard.html'
