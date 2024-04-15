from django.contrib import admin
from accounts.models import User


class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_active', 'is_admin')


admin.site.register(User, UserAccountAdmin)
