from django.db.models.query import QuerySet
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from core.models import Location, Trip, Vehicle
from django.utils import timezone
from django.contrib import messages

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


class RentVehicleView(LoginRequiredMixin, CreateView):
    def post(self, request, code, *arg, **kwargs):
        vehicle = get_object_or_404(Vehicle, code=code, status=Vehicle.Status.AVAILABLE)
        trip = Trip.objects.create(
            user=request.user,
            vehicle=vehicle,
            start_time=timezone.now(),
            start_location=vehicle.location,
            status=Trip.Status.IN_PROGRESS,
        )

        vehicle.status = Vehicle.Status.IN_USE
        vehicle.save(update_fields=['status'])

        messages.success(request, f'You have successfully rented {vehicle.type.model}.')

        return redirect('trip_detail', pk=trip.pk)


class TripDetailView(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'customers/trip_detail.html'
    context_object_name = 'trip'

    def get_queryset(self) -> QuerySet[Trip]:
        return super().get_queryset().filter(user=self.request.user)
