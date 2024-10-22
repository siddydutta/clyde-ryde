from collections import defaultdict

from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from core.models import Trip, Vehicle
from managers.mixins import DateFilterMixin, LoginRequiredMixin
from users.models import CustomUser
from users.views import BaseUserLoginView


class LoginView(BaseUserLoginView):
    success_url = reverse_lazy('manager_dashboard')
    user_type = CustomUser.Type.MANAGER


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'managers/dashboard.html'


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
