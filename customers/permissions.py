from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect

from customers.models import Address


class DeleteAddressPermission:
    def dispatch(self, request, *args, **kwargs):
        if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
            return redirect('accounts:login')
        address_id = self.kwargs.get('pk')
        address = get_object_or_404(Address, pk=address_id)
        if address.customer not in self.request.user.customers.all():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)
