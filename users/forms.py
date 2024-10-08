from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import CustomUser


class BaseCustomUserCreationForm(UserCreationForm):
    def __init__(self, user_type: CustomUser.UserType, *args, **kwargs):
        self.user_type = user_type
        super().__init__(*args, **kwargs)

    email = forms.EmailField(required=True)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = self.user_type
        if commit:
            user.save()
        return user

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'password1',
            'password2',
        )


class CustomerRegistrationForm(BaseCustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(CustomUser.UserType.CUSTOMER, *args, **kwargs)


class OperatorRegistrationForm(BaseCustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(CustomUser.UserType.OPERATOR, *args, **kwargs)


class ManagerRegistrationForm(BaseCustomUserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(CustomUser.UserType.MANAGER, *args, **kwargs)
