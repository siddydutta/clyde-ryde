from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CustomerRegistrationForm


class CustomerRegisterView(CreateView):
    form_class = CustomerRegistrationForm
    template_name = 'customer/register.html'
    success_url = 'http://localhost:8000'
    # success_url = reverse_lazy('customer_dashboard')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
