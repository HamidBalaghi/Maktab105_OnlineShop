from .models import User
from django.contrib.auth.backends import ModelBackend as BaseBackend


class ModelBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            if password and not user.check_password(password):
                return None
            return user

        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username)
                if password and not user.check_password(password):
                    return None
                return user
            except User.DoesNotExist:
                return None
