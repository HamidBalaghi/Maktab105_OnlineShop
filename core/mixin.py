from django.contrib.auth.models import AnonymousUser


class NavbarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated and not isinstance(user, AnonymousUser):
            context['logged_in_user'] = user
            context['logged_in_user_pk'] = user.pk
        else:
            context['current_url'] = self.request.build_absolute_uri()
        return context
