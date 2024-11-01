from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from core.models import Location, Trip, Vehicle
from customers.forms import ReturnVehicleForm
from customers.mixins import LoginRequiredMixin
from customers.models import Payment
from users.models import CustomUser
from users.views import BaseUserLoginView


class LoginView(BaseUserLoginView):
    success_url = reverse_lazy('customer_dashboard')
    user_type = CustomUser.Type.CUSTOMER


class DashboardView(LoginRequiredMixin, ListView):
    template_name = 'customers/dashboard.html'
    model = Trip
    queryset = Trip.objects.select_related('start_location', 'payment')
    context_object_name = 'trips'
    paginate_by = 10
    ordering = '-start_time'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class Wallet(LoginRequiredMixin, ListView):
    template_name = 'customers/wallet.html'
    model = Payment
    context_object_name = 'payments'
    paginate_by = 10
    ordering = '-created_at'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(trip__user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['outstanding'] = Payment.objects.filter(
            trip__user=self.request.user, status=Payment.Status.PENDING
        ).aggregate(total=Sum('amount'))['total']
        print(context['outstanding'])
        return context

    def post(self, request):
        amount = request.POST.get('amount')
        if amount:
            with transaction.atomic():
                request.user.wallet.balance += Decimal(amount)
                request.user.wallet.save(update_fields=['balance', 'updated_at'])
                messages.success(
                    request,
                    _('You have successfully topped up £%(amount)s.')
                    % {'amount': amount},
                )
        return redirect('wallet')


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
        vehicle.save(update_fields=['status'])
        messages.success(
            request,
            _('You have successfully rented %(model)s.')
            % {'model': vehicle.type.model},
        )
        return redirect('trip_detail', pk=trip.pk)


class TripDetailView(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'customers/trip_detail.html'
    context_object_name = 'trip'
    queryset = Trip.objects.select_related(
        'vehicle__type', 'start_location', 'end_location', 'payment'
    )

    def get_queryset(self):
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
                            _('Trip completed! You have been charged £%(trip_cost).2f.')
                            % {'trip_cost': trip_cost},
                        )
                    else:
                        messages.error(
                            request,
                            _('Insufficient balance. Please top-up your wallet.'),
                        )
        return redirect('trip_detail', pk=trip.pk)


class ReportVehicleView(LoginRequiredMixin, View):
    def post(self, request, trip_id: int):
        trip = get_object_or_404(Trip, id=trip_id, user=request.user)
        if trip.vehicle.status == Vehicle.Status.DEFECTIVE:
            messages.error(request, _('The vehicle is already reported!'))
        else:
            trip.vehicle.status = Vehicle.Status.DEFECTIVE
            trip.vehicle.save(update_fields=['status'])
            messages.success(request, _('The vehicle has been reported as defective.'))
        return redirect('trip_detail', pk=trip.pk)


class TripPayment(LoginRequiredMixin, View):
    def post(self, request, trip_id: int, payment_id: int):
        payment = get_object_or_404(Payment, id=payment_id)
        trip_cost = payment.trip.compute_cost()
        with transaction.atomic():
            if request.user.wallet.debit(trip_cost):
                payment.complete_payment()
                messages.success(
                    request,
                    _('You have been charged £%(trip_cost).2f.')
                    % {'trip_cost': trip_cost},
                )
            else:
                messages.error(
                    request, _('Insufficient balance. Please top-up your wallet.')
                )
        return redirect('trip_detail', pk=payment.trip.pk)
