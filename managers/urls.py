from django.urls import path
from managers.views import DashboardView, LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='manager_login'),
    path('', DashboardView.as_view(), name='manager_dashboard'),
]
