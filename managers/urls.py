from django.urls import path
from managers.views import (
    DashboardView,
    LoginView,
    TripDurationView,
    VehicleCountView,
    VehicleUsageView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='manager_login'),
    path('', DashboardView.as_view(), name='manager_dashboard'),
    path('trip-duration/', TripDurationView.as_view(), name='trip_duration'),
    path('vehicle-count/', VehicleCountView.as_view(), name='vehicle_count'),
    path('vehicle-usage/', VehicleUsageView.as_view(), name='vehicle_usage'),
]
