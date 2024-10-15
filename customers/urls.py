from django.urls import path
from customers.views import (
    LocationListView,
    LocationDetailView,
    DashboardView,
    LoginView,
    RentVehicleView,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='customer_login'),
    path('', DashboardView.as_view(), name='customer_dashboard'),
    path('locations/', LocationListView.as_view(), name='location_list'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location_detail'),
    path('rent/<int:vehicle_code>/', RentVehicleView.as_view(), name='rent_vehicle'),
]
