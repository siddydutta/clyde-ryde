from django.db.models.query import QuerySet
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from core.models import Location, Trip, Vehicle
from django.utils import timezone
from django.contrib import messages
from django.views import View
from customers.forms import ReturnVehicleForm

from customers.mixins import LoginRequiredMixin
from customers.models import Payment
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
    def post(self, request, code: int):
        vehicle = get_object_or_404(Vehicle, code=code, status=Vehicle.Status.AVAILABLE)
        trip = Trip.objects.create(
            user=request.user,
            vehicle=vehicle,
            start_time=timezone.now(),
            start_location=vehicle.location,
            status=Trip.Status.IN_PROGRESS,
        )

        vehicle.status = Vehicle.Status.IN_USE
        vehicle.save()

        messages.success(request, f'You have successfully rented {vehicle.type.model}.')

        return redirect('trip_detail', pk=trip.pk)


class TripDetailView(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'customers/trip_detail.html'
    context_object_name = 'trip'

    def get_queryset(self) -> QuerySet[Trip]:
        return super().get_queryset().filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['return_vehicle_form'] = ReturnVehicleForm()
        return context


class ReturnVehicleView(LoginRequiredMixin, View):
    def post(self, request, trip_id: int):
        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        if trip.end_time is None:
            form = ReturnVehicleForm(request.POST, instance=trip)
            if form.is_valid():
                trip.end_trip(form.cleaned_data['end_location'])
                trip_cost = trip.compute_cost()
                payment = Payment.objects.create(trip=trip, amount=trip_cost)
                if request.user.wallet.debit(trip_cost):
                    payment.status = Payment.Status.COMPLETED
                    payment.paid_at = timezone.now()
                    payment.save(update_fields=['status', 'paid_at'])
                    messages.success(
                        request,
                        f'Trip completed! You have been charged {trip_cost:.2f}.',
                    )
                else:
                    messages.error(
                        request, 'Insufficient balance. Please top-up your wallet.'
                    )
                return redirect('trip_detail', pk=trip.pk)
        return redirect('trip_detail', pk=trip.pk)


class ReportVehicleView(LoginRequiredMixin, View):
    def post(self, request, trip_id: int):
        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        if trip.vehicle.status == Vehicle.Status.DEFECTIVE:
            messages.error(request, 'The vehicle is already reported!')
        else:
            trip.vehicle.status = Vehicle.Status.DEFECTIVE
            trip.vehicle.save()
            messages.success(request, 'The vehicle has been reported as defective.')
        return redirect('trip_detail', pk=trip.pk)
