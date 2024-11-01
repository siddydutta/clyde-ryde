from django.urls import path

from customers.views import (
    DashboardView,
    LocationDetailView,
    LocationListView,
    LoginView,
    RentVehicleView,
    ReportVehicleView,
    ReturnVehicleView,
    TripDetailView,
    TripPayment,
    Wallet,
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='customer_login'),
    path('', DashboardView.as_view(), name='customer_dashboard'),
    path('locations/', LocationListView.as_view(), name='location_list'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location_detail'),
    path('rent/<int:code>/', RentVehicleView.as_view(), name='rent_vehicle'),
    path('trips/<int:pk>/', TripDetailView.as_view(), name='trip_detail'),
    path(
        'trip/<int:trip_id>/return/', ReturnVehicleView.as_view(), name='return_vehicle'
    ),
    path(
        'trip/<int:trip_id>/report/', ReportVehicleView.as_view(), name='report_vehicle'
    ),
    path(
        'trip/<int:trip_id>/pay/<int:payment_id>/',
        TripPayment.as_view(),
        name='trip_payment',
    ),
    path('wallet/', Wallet.as_view(), name='wallet'),
]
