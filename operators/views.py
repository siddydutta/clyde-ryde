from django.contrib import messages
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, TemplateView

from core.models import Location, Vehicle
from operators.mixins import LoginRequiredMixin
from users.models import CustomUser
from users.views import BaseUserLoginView


class LoginView(BaseUserLoginView):
    success_url = reverse_lazy('operator_dashboard')
    user_type = CustomUser.Type.OPERATOR


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'operators/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations_count'] = Location.objects.count()
        context['vehicles_count'] = Vehicle.objects.count()
        context['vehicle_status_count'] = {
            item['status']: item['count']
            for item in Vehicle.objects.values('status').annotate(count=Count('status'))
        }
        return context


class VehicleListView(ListView):
    template_name = 'operators/vehicle_list.html'
    model = Vehicle
    queryset = Vehicle.objects.select_related('type', 'location')
    context_object_name = 'vehicles'
    paginate_by = 10
    ordering = 'code'

    def get_queryset(self):
        queryset = super().get_queryset()
        # filtering
        status_filter = self.request.GET.get('status')
        location_filter = self.request.GET.get('location')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if location_filter:
            queryset = queryset.filter(location__name__icontains=location_filter)

        # ordering
        order_param = self.request.GET.get('sort')
        order_type = self.request.GET.get('order')
        if order_param:
            order_param = f'-{order_param}' if order_type == 'desc' else order_param
            queryset = queryset.order_by(order_param)
        return queryset

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['statuses'] = Vehicle.Status.choices
        return context


class VehicleDetailView(DetailView):
    model = Vehicle
    template_name = 'operators/vehicle_detail.html'
    context_object_name = 'vehicle'
    queryset = Vehicle.objects.all().select_related('location')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['locations'] = Location.objects.only('id', 'name').exclude(
            id=self.object.location_id
        )
        return context

    def get_success_url(self):
        return self.request.path

    def post(self, request, *args, **kwargs):
        vehicle = self.get_object()
        if vehicle.status == Vehicle.Status.IN_USE:
            messages.error(request, 'Vehicle is currently in use!')
            return redirect(self.get_success_url())

        if 'charge' in request.POST:
            if vehicle.status == Vehicle.Status.DISCHARGED:
                vehicle.status = Vehicle.Status.AVAILABLE
            vehicle.battery_level = 100
            messages.success(
                request,
                _('Vehicle %(code)s is charged to 100%%!') % {'code': vehicle.code},
            )
        if 'repair' in request.POST and vehicle.status == 'defective':
            vehicle.status = Vehicle.Status.AVAILABLE
            messages.success(
                request, _('Vehicle %(code)s is repaired!') % {'code': vehicle.code}
            )
        if 'change_location' in request.POST and vehicle.status != 'in_use':
            new_location_id = request.POST.get('new_location')
            vehicle.location_id = new_location_id
            messages.success(
                request, _('Vehicle %(code)s is moved!') % {'code': vehicle.code}
            )
        vehicle.save()
        return redirect(self.get_success_url())
