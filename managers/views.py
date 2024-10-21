from django.db.models import Count
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from core.models import Trip
from managers.mixins import DateFilterMixin, LoginRequiredMixin
from users.models import CustomUser
from users.views import BaseUserLoginView


class LoginView(BaseUserLoginView):
    success_url = reverse_lazy('manager_dashboard')
    user_type = CustomUser.Type.MANAGER


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'managers/dashboard.html'


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
