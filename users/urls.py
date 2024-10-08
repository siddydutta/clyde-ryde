from django.urls import path

from users.views import CustomerRegisterView

urlpatterns = [
    path('register/', CustomerRegisterView.as_view(), name='register'),
]
