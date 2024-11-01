from django.urls import path

from operators.views import DashboardView, LoginView, VehicleDetailView, VehicleListView

urlpatterns = [
    path('login/', LoginView.as_view(), name='operator_login'),
    path('', DashboardView.as_view(), name='operator_dashboard'),
    path('vehicles/', VehicleListView.as_view(), name='vehicle_list'),
    path('vehicles/<int:pk>/', VehicleDetailView.as_view(), name='vehicle_detail'),
]
