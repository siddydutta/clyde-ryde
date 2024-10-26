from django.db.models import Prefetch
from django.db.models.query import QuerySet
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import CreateView
from django.conf import settings
from django.db import transaction
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return context


class LocationDetailView(LoginRequiredMixin, DetailView):
    model = Location
    template_name = 'customers/location_detail.html'
    context_object_name = 'location'
    queryset = Location.objects.only('name', 'address')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model_filters'] = self.object.vehicles.values_list(
            'type_id', 'type__model'
        ).distinct()
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        vehicle_qs = (
            Vehicle.objects.only(
                'code',
                'battery_level',
                'location_id',
                'type__model',
                'type__brand',
                'type__rate',
                'type__image',
            )
            .select_related('type')
            .filter(status=Vehicle.Status.AVAILABLE)
        )
        sort, filter = self.request.GET.get('sort'), self.request.GET.get('filter')
        if sort == 'rate':
            vehicle_qs = vehicle_qs.order_by('type__rate')
        elif sort == 'battery_level':
            vehicle_qs = vehicle_qs.order_by('-battery_level')
        if filter:
            vehicle_qs = vehicle_qs.filter(type_id=filter)
        queryset = queryset.prefetch_related(
            Prefetch('vehicles', queryset=vehicle_qs, to_attr='available_vehicles')
        )
        return queryset


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
                with transaction.atomic():
                    if request.user.wallet.debit(trip_cost):
                        payment.complete_payment()
                        messages.success(
                            request,
                            f'Trip completed! You have been charged {trip_cost:.2f}.',
                        )
                    else:
                        messages.error(
                            request, 'Insufficient balance. Please top-up your wallet.'
                        )
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


class TripPayment(LoginRequiredMixin, View):
    def post(self, request, trip_id: int, payment_id: int):
        payment = get_object_or_404(Payment, id=payment_id)
        trip_cost = payment.trip.compute_cost()
        if request.user.wallet.debit(trip_cost):
            payment.complete_payment()
            messages.success(
                request,
                f'You have been charged {trip_cost:.2f}.',
            )
        else:
            messages.error(request, 'Insufficient balance. Please top-up your wallet.')
        return redirect('trip_detail', pk=payment.trip.pk)
