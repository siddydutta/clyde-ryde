from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, DetailView

from core.models import Location, Vehicle
from operators.mixins import LoginRequiredMixin
from users.models import CustomUser
from users.views import BaseUserLoginView

from django.contrib import messages
from django.shortcuts import redirect


class LoginView(BaseUserLoginView):
    success_url = reverse_lazy('operator_dashboard')
    user_type = CustomUser.Type.OPERATOR


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'operators/dashboard.html'


class VehicleListView(ListView):
    model = Vehicle
    template_name = 'operators/vehicle_list.html'
    context_object_name = 'vehicles'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.GET.get('status')
        location_filter = self.request.GET.get('location')

        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if location_filter:
            queryset = queryset.filter(location__name__icontains=location_filter)

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
            id=context['vehicle'].location_id
        )
        return context

    def post(self, request, *args, **kwargs):
        vehicle = self.get_object()
        if 'charge' in request.POST:
            vehicle.battery_level = 100
            vehicle.save()
            messages.success(request, f'Vehicle {vehicle.code} charged to 100%!')
            return redirect(self.get_success_url())

        if 'repair' in request.POST and vehicle.status == 'defective':
            vehicle.status = Vehicle.Status.AVAILABLE
            vehicle.save()
            messages.success(
                request, f'Vehicle {vehicle.code} status updated to Available!'
            )
            return redirect(self.get_success_url())

        if 'change_location' in request.POST and vehicle.status != 'in_use':
            new_location_id = request.POST.get('new_location')
            vehicle.location_id = new_location_id
            vehicle.save()
            messages.success(request, f'Vehicle {vehicle.code} moved to new location!')
            return redirect(self.get_success_url())

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.path
