from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


from .forms import CustomerRegistrationForm


class CustomerRegisterView(CreateView):
    form_class = CustomerRegistrationForm
    template_name = 'customer/register.html'
    success_url = reverse_lazy('customer_dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect(self.success_url)


class CustomerLoginView(LoginView):
    template_name = 'customer/login.html'
    success_url = reverse_lazy('customer_dashboard')

    def get_success_url(self):
        return self.success_url


class CustomerLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, _('You have been successfully logged out.'))
        return super().dispatch(request, *args, **kwargs)


class CustomerDashboardView(TemplateView):
    template_name = 'customer/dashboard.html'
