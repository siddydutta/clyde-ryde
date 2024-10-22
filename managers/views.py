from collections import defaultdict
from itertools import accumulate
import numpy as np

from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from core.models import Trip, Vehicle
from customers.models import Payment
from managers.mixins import DateFilterMixin, LoginRequiredMixin
from users.models import CustomUser
from users.views import BaseUserLoginView


class LoginView(BaseUserLoginView):
    success_url = reverse_lazy('manager_dashboard')
    user_type = CustomUser.Type.MANAGER


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'managers/dashboard.html'


class RevenueView(LoginRequiredMixin, DateFilterMixin, TemplateView):
    template_name = 'managers/revenue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from_date, to_date = self.get_date_range()
        query = (
            Payment.objects.filter(
                status=Payment.Status.COMPLETED,
                paid_at__date__range=[from_date, to_date],
            )
            .annotate(date=TruncDate('paid_at'))
            .values('date')
            .annotate(daily_revenue=Sum('amount'))
            .order_by('date')
        )

        dates = [payment['date'].strftime('%Y-%m-%d') for payment in query]
        daily_revenues = [float(payment['daily_revenue']) for payment in query]
        cumulative_revenues = list(accumulate(daily_revenues))

        context['dates'] = dates
        context['daily_revenues'] = daily_revenues
        context['cumulative_revenues'] = cumulative_revenues
        context['from_date'] = str(from_date)
        context['to_date'] = str(to_date)
        return context


class TripDurationView(LoginRequiredMixin, DateFilterMixin, TemplateView):
    template_name = 'managers/trip_duration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from_date, to_date = self.get_date_range()

        query = Trip.objects.only('start_time', 'end_time').filter(
            start_time__date__range=[from_date, to_date], status=Trip.Status.COMPLETED
        )
        trip_durations = [trip.duration / 60 for trip in query]
        bin_edges = np.arange(0, max(trip_durations) + 10, 30)  # bins of 30 minutes
        hist, bin_edges = np.histogram(trip_durations, bins=bin_edges)

        context['from_date'] = str(from_date)
        context['to_date'] = str(to_date)
        context['bin_edges'] = bin_edges[:-1].tolist()
        context['hist'] = hist.tolist()
        return context


class VehicleCountView(LoginRequiredMixin, TemplateView):
    template_name = 'managers/vehicle_count.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = (
            Vehicle.objects.filter(~Q(status=Vehicle.Status.IN_USE))
            .select_related('location')
            .values('location__name', 'status')
            .annotate(count=Count('code'))
        )

        location_data = defaultdict(
            lambda: {Vehicle.Status.AVAILABLE: 0, Vehicle.Status.DEFECTIVE: 0}
        )
        for item in query:
            location_data[item['location__name']][item['status']] = item['count']
        locations = []
        available_counts = []
        defective_counts = []
        for location_name, counts in location_data.items():
            locations.append(location_name)
            available_counts.append(counts['available'])
            defective_counts.append(counts['defective'])

        context['locations'] = locations
        context['available_counts'] = available_counts
        context['defective_counts'] = defective_counts
        return context


class VehicleUsageView(LoginRequiredMixin, DateFilterMixin, TemplateView):
    template_name = 'managers/vehicle_usage.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from_date, to_date = self.get_date_range()

        query = (
            Trip.objects.filter(
                status=Trip.Status.COMPLETED,
                start_time__date__range=[from_date, to_date],
            )
            .select_related('vehicle__type')
            .values('vehicle__type__model')
            .annotate(count=Count('id'))
        )
        models, counts = [], []
        for item in query:
            models.append(item['vehicle__type__model'])
            counts.append(item['count'])

        context['from_date'] = str(from_date)
        context['to_date'] = str(to_date)
        context['models'] = models
        context['counts'] = counts
        return context
