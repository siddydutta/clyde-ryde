from django.urls import path

from users.views import (
    CustomerRegisterView,
    CustomerDashboardView,
    CustomerLoginView,
    CustomerLogoutView,
)

urlpatterns = [
    path('register/', CustomerRegisterView.as_view(), name='customer_register'),
    path('login/', CustomerLoginView.as_view(), name='customer_login'),
    path('logout/', CustomerLogoutView.as_view(), name='customer_logout'),
    path('', CustomerDashboardView.as_view(), name='customer_dashboard'),
]
