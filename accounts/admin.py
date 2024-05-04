from django.contrib import admin
from accounts.models import User


class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_superuser', 'is_staff', 'is_active', 'is_deleted')
    list_filter = ('is_active', 'is_staff', 'is_deleted')
    search_fields = ('username', 'email')
    ordering = ('is_deleted', 'is_active', 'is_staff', 'username', 'created_at')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return User.global_objects.all()


admin.site.register(User, UserAccountAdmin)
