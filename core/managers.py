from django.db import models


class LogicalManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False, is_active=True)

    @property
    def archived(self):
        return super().get_queryset()
