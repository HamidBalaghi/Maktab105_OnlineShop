from django.db import models
from .managers import LogicalManager


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LogicalMixin(models.Model):
    """
    Logical model mixin:

    fields:
        - is_active: BooleanField (default True)
        - is_deleted: BooleanField (default False)
    """

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    objects = LogicalManager()
    global_objects = models.Manager()

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.save(update_fields=["is_deleted"])

    def undelete(self, using=None, keep_parents=False):
        self.is_deleted = False
        self.save(update_fields=["is_deleted"])

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=["is_active"])

    @classmethod
    def delete_queryset(cls, queryset):
        queryset.update(is_deleted=True)

    @classmethod
    def undelete_queryset(cls, queryset):
        queryset.update(is_deleted=False)

    class Meta:
        abstract = True
