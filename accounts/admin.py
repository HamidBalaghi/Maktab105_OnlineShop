from django.contrib import admin
from accounts.models import User,OTPModel


class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_active', 'is_admin', 'is_deleted')


admin.site.register(User, UserAccountAdmin)


class OTPModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')


admin.site.register(OTPModel, OTPModelAdmin)
