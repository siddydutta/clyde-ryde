from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404
from core.models import Location, Vehicle
from django.utils import timezone

from customers.mixins import LoginRequiredMixin
from users.models import CustomUser
from users.views import BaseUserLoginView


class LoginView(BaseUserLoginView):
    success_url = reverse_lazy('customer_dashboard')
    user_type = CustomUser.Type.CUSTOMER


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'customers/dashboard.html'


class LocationListView(LoginRequiredMixin, ListView):
    model = Location
    template_name = 'customers/location_list.html'
    context_object_name = 'locations'


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    template_name = 'customers/location_detail.html'
    context_object_name = 'location'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_vehicles'] = self.object.vehicles.filter(status='available')
        return context


# class RentVehicleView(LoginRequiredMixin, CreateView):
#     model = Rental
#     fields = ['vehicle']
#     template_name = 'customers/rent_vehicle.html'
#     success_url = reverse_lazy('customer_dashboard')

#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         form.instance.start_location = form.instance.vehicle.location
#         form.instance.vehicle.status = 'IN_USE'
#         form.instance.vehicle.save()
#         return super().form_valid(form)

#     def get_form(self, form_class=None):
#         form = super().get_form(form_class)
#         location = get_object_or_404(Location, pk=self.kwargs['location_id'])
#         form.fields['vehicle'].queryset = Vehicle.objects.filter(location=location, status='AVAILABLE')
#         return form
