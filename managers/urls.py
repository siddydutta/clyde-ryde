from django.urls import path
from managers.views import DashboardView, LoginView, VehicleUsageView

urlpatterns = [
    path('login/', LoginView.as_view(), name='manager_login'),
    path('', DashboardView.as_view(), name='manager_dashboard'),
    path('vehicle-usage/', VehicleUsageView.as_view(), name='vehicle_usage'),
]
