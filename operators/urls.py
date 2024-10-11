from django.urls import path
from operators.views import DashboardView, LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='operator_login'),
    path('', DashboardView.as_view(), name='operator_dashboard'),
]
