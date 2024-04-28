from django.contrib import admin
from accounts.models import User


class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_superuser', 'is_staff', 'is_active', 'is_deleted')


admin.site.register(User, UserAccountAdmin)
