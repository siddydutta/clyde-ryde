from django.contrib import admin

from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'type',
    )
    list_filter = ('type',)
    search_fields = (
        'username__startsiwth',
        'email__startswith',
    )
