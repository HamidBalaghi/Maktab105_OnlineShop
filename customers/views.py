from django.shortcuts import redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, View
from .forms import EditProfileForm, CustomPasswordChangeForm, NewAddressForm
from .models import Customer, Address
from accounts.models import User
from django.db import IntegrityError
from accounts.tasks import otp_sender
from django.core.cache import cache
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from core.mixin import NavbarMixin, LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from .permissions import DeleteAddressPermission
from orders.models import Order


class EditProfileView(NavbarMixin, TemplateView):
    template_name = 'customers/editprofile.html'

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        # Login Required
        if isinstance(request.user, AnonymousUser) or not request.user.is_authenticated:
            return redirect('accounts:login')

        self.customer = Customer.objects.get(customer=self.user)
        # Initialize fields of form
        email = self.user.email
        username = self.user.username
        phone = Customer.objects.get(customer=self.user).phone_number
        name = Customer.objects.get(customer=self.user).full_name
        temp = dict()
        temp['name'] = name
        temp['email'] = email
        temp['phone'] = phone
        temp['username'] = username
        self.temp = temp

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['initial'] = self.temp
        return context

    def get(self, request, *args, **kwargs):
        form = EditProfileForm()
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = EditProfileForm(request.POST)
        if form.is_valid():
            # change Full name and Phone number
            self.customer.full_name = form.cleaned_data['name']
            self.customer.phone_number = form.cleaned_data['phone']
            self.customer.save()

            new_username = form.cleaned_data['username']
            new_email = form.cleaned_data['email']

            # Change username field
            try:
                self.user.username = new_username
                self.user.save()
            except IntegrityError:
                form.add_error('username', "Username already exists")
                return self.render_to_response({'form': form, 'initial': self.temp})

            # Change email field
            if new_email != self.user.email:
                check_email = User.objects.filter(email=new_email).first()
                if check_email:
                    form.add_error('email', "Email already exists!")
                    return self.render_to_response({'form': form, 'initial': self.temp})
                else:

                    # Redirect to Verification
                    otp_sender.delay(email=new_email, username=new_username)
                    cache.set(f"{self.user.pk}", new_email, timeout=300)
                    return redirect('accounts:activation', pk=self.user.pk)
            return redirect('customers:profile')
        return self.render_to_response({'form': form, 'initial': self.temp})


class ProfileView(LoginRequiredMixin, NavbarMixin, TemplateView):
    template_name = 'customers/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.user.email
        context['username'] = self.request.user.username
        context['name'] = Customer.objects.get(customer=self.request.user).full_name
        context['phone'] = Customer.objects.get(customer=self.request.user).phone_number
        context['paid_orders_count'] = Order.objects.filter(customer__customer=self.request.user, is_paid=True).count()

        return context


class CustomPasswordChangeView(LoginRequiredMixin, NavbarMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'customers/change-password.html'
    success_url = reverse_lazy('customers:profile')


class AddNewAddressView(LoginRequiredMixin, NavbarMixin, CreateView):
    template_name = 'customers/new-address.html'
    form_class = NewAddressForm

    def get_success_url(self):
        next_url = self.request.COOKIES.get('next_url_checkout')
        if next_url:
            return reverse_lazy('orders:checkout')
        return reverse_lazy('customers:address')

    def form_valid(self, form):
        customer = Customer.objects.get(customer=self.request.user)
        form.instance.customer = customer

        return super().form_valid(form)


class ShowAddressView(LoginRequiredMixin, NavbarMixin, TemplateView):
    template_name = 'customers/addresses.html'

    def get_context_data(self, **kwargs):
        customer = Customer.objects.get(customer=self.request.user)
        context = super().get_context_data(**kwargs)
        context['addresses'] = customer.addresses.all().order_by('-created_at')
        return context


class DeleteAddressView(DeleteAddressPermission, NavbarMixin, View):

    def get(self, request, *args, **kwargs):
        address = get_object_or_404(Address, pk=self.kwargs['pk'])
        address.delete()
        return redirect('customers:address')
