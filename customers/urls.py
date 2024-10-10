from django.urls import path
from customers.views import LocationListView, LocationDetailView

urlpatterns = [
    path('locations/', LocationListView.as_view(), name='location_list'),
    path('locations/<int:pk>/', LocationDetailView.as_view(), name='location_detail'),
    # path('rent/<int:location_id>/', RentVehicleView.as_view(), name='rent_vehicle'),
]
