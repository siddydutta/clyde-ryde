from collections import defaultdict
from itertools import accumulate
import csv
import numpy as np

from django.conf import settings
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDate
from django.http.response import HttpResponse as HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from core.models import Trip, Vehicle
from customers.models import Payment, Wallet
from managers.mixins import DateFilterMixin, LoginRequiredMixin
from users.models import CustomUser
from users.views import BaseUserLoginView


class LoginView(BaseUserLoginView):
    success_url = reverse_lazy('manager_dashboard')
    user_type = CustomUser.Type.MANAGER


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'managers/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers_count'] = CustomUser.objects.filter(
            type=CustomUser.Type.CUSTOMER
        ).count()
        context['operators_count'] = CustomUser.objects.filter(
            type=CustomUser.Type.OPERATOR
        ).count()
        context['managers_count'] = CustomUser.objects.filter(
            type=CustomUser.Type.MANAGER
        ).count()
        context['total_revenue'] = (
            Payment.objects.filter(status=Payment.Status.COMPLETED).aggregate(
                Sum('amount')
            )['amount__sum']
            or 0
        )
        context['total_wallet_balance'] = (
            Wallet.objects.aggregate(Sum('balance'))['balance__sum'] or 0
        )
        context['total_trips'] = Trip.objects.count()
        return context


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

        context['from_date'] = str(from_date)
        context['to_date'] = str(to_date)
        context['dates'] = dates
        context['daily_revenues'] = daily_revenues
        context['cumulative_revenues'] = cumulative_revenues
        return context

    def render_to_response(self, context, **response_kwargs) -> HttpResponse:
        if self.request.GET.get('download') == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = (
                'attachment; filename="revenue_report.csv"'
            )
            writer = csv.writer(response)
            writer.writerow(['Date', 'Daily Revenue', 'Cumulative Revenue'])
            for date, daily_revenue, cumulative_revenue in zip(
                context['dates'],
                context['daily_revenues'],
                context['cumulative_revenues'],
            ):
                writer.writerow([date, daily_revenue, cumulative_revenue])
            return response
        return super().render_to_response(context, **response_kwargs)


class LocationPopularity(LoginRequiredMixin, DateFilterMixin, TemplateView):
    template_name = 'managers/location_popularity.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from_date, to_date = self.get_date_range()

        query = (
            Trip.objects.filter(
                start_time__date__range=[from_date, to_date],
                status=Trip.Status.COMPLETED,
            )
            .values('start_location__latitude', 'start_location__longitude')
            .annotate(count=Count('id'))
        )

        context['from_date'] = str(from_date)
        context['to_date'] = str(to_date)
        context['locations'] = query
        context['GOOGLE_MAPS_API_KEY'] = settings.GOOGLE_MAPS_API_KEY
        return context

    def render_to_response(self, context, **response_kwargs) -> HttpResponse:
        if self.request.GET.get('download') == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = (
                'attachment; filename="location_popularity_report.csv"'
            )
            writer = csv.writer(response)
            writer.writerow(['Latitude', 'Longitude', 'Count'])
            for location in context['locations']:
                writer.writerow(
                    [
                        location['start_location__latitude'],
                        location['start_location__longitude'],
                        location['count'],
                    ]
                )
            return response
        return super().render_to_response(context, **response_kwargs)


class TripDurationView(LoginRequiredMixin, DateFilterMixin, TemplateView):
    template_name = 'managers/trip_duration.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from_date, to_date = self.get_date_range()

        query = Trip.objects.only('start_time', 'end_time').filter(
            start_time__date__range=[from_date, to_date], status=Trip.Status.COMPLETED
        )
        trip_durations = [trip.duration / 60 for trip in query] or [0]
        bin_edges = np.arange(0, max(trip_durations) + 10, 30)  # bins of 30 minutes
        hist, bin_edges = np.histogram(trip_durations, bins=bin_edges)
        intervals = []
        for x, y in zip(bin_edges[:-1], bin_edges[1:]):
            intervals.append(f'{round(x)} - {round(y)}')

        context['from_date'] = str(from_date)
        context['to_date'] = str(to_date)
        context['intervals'] = intervals
        context['hist'] = hist.tolist()
        return context

    def render_to_response(self, context, **response_kwargs) -> HttpResponse:
        if self.request.GET.get('download') == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = (
                'attachment; filename="trip_duration_report.csv"'
            )
            writer = csv.writer(response)
            writer.writerow(['Duration (minutes)', 'Count'])
            for duration, count in zip(context['intervals'], context['hist']):
                writer.writerow([duration, count])
            return response
        return super().render_to_response(context, **response_kwargs)


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

    def render_to_response(self, context, **response_kwargs) -> HttpResponse:
        if self.request.GET.get('download') == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = (
                'attachment; filename="vehicle_count_report.csv"'
            )
            writer = csv.writer(response)
            writer.writerow(['Location', 'Available Count', 'Defective Count'])
            for location, available_count, defective_count in zip(
                context['locations'],
                context['available_counts'],
                context['defective_counts'],
            ):
                writer.writerow([location, available_count, defective_count])
            return response
        return super().render_to_response(context, **response_kwargs)


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

    def render_to_response(self, context, **response_kwargs) -> HttpResponse:
        if self.request.GET.get('download') == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = (
                'attachment; filename="vehicle_usage_report.csv"'
            )
            writer = csv.writer(response)
            writer.writerow(['Model', 'Count'])
            for model, count in zip(context['models'], context['counts']):
                writer.writerow([model, count])
            return response
        return super().render_to_response(context, **response_kwargs)
