from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from .forms import EditProfileForm, CustomPasswordChangeForm
from .models import Customer
from accounts.models import User
from django.db import IntegrityError
from accounts.tasks import otp_sender
from django.core.cache import cache
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from core.mixin import NavbarMixin


class EditProfileView(NavbarMixin, TemplateView):
    template_name = 'customers/editprofile.html'

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
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


class ProfileView(NavbarMixin, TemplateView):
    template_name = 'customers/profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = self.request.user.email
        context['username'] = self.request.user.username
        context['name'] = Customer.objects.get(customer=self.request.user).full_name
        context['phone'] = Customer.objects.get(customer=self.request.user).phone_number
        return context


class CustomPasswordChangeView(NavbarMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'customers/change-password.html'
    success_url = reverse_lazy('customers:profile')
