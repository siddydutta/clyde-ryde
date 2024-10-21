from datetime import date, timedelta
from django.urls import reverse_lazy
from django.utils import timezone

from users.mixins import BaseLoginRequiredMixin
from users.models import CustomUser


class LoginRequiredMixin(BaseLoginRequiredMixin):
    user_type = CustomUser.Type.MANAGER
    login_url = reverse_lazy('manager_login')


class DateFilterMixin:
    def get_date_range(self):
        from_date = self.request.GET.get('from_date')
        to_date = self.request.GET.get('to_date')
        if from_date and to_date:
            from_date, to_date = map(self.format_date, (from_date, to_date))
        else:
            from_date = timezone.now().date() - timedelta(days=7)
            to_date = timezone.now().date()
        return from_date, to_date

    @staticmethod
    def format_date(date: str) -> date:
        return timezone.datetime.strptime(date, '%Y-%m-%d').date()
