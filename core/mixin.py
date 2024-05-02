class NavbarMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['logged_in_user'] = user
        context['logged_in_user_pk'] = user.pk
        return context