from django.contrib import admin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = (
        'username',
        'email',
        'user_type',
    )
    list_filter = ('user_type',)
    search_fields = (
        'username__startsiwth',
        'email__startswith',
    )
