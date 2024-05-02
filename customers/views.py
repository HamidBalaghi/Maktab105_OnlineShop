from django.shortcuts import render, redirect
from django.views import View
from .forms import EditProfileForm
from .models import Customer
from accounts.models import User
from django.db import IntegrityError
from accounts.tasks import otp_sender
from django.core.cache import cache


class EditProfileView(View):
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

    def get(self, request, *args, **kwargs):
        form = EditProfileForm()
        return render(request, self.template_name, {'form': form, 'initial': self.temp})

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
                return render(request, self.template_name, {'form': form, 'initial': self.temp})

            # Change email field
            if new_email != self.user.email:
                check_email = User.objects.filter(email=new_email).first()
                if check_email:
                    form.add_error('email', "Email already exists!")
                    return render(request, self.template_name, {'form': form, 'initial': self.temp})
                else:

                    # Redirect to Verification
                    otp_sender.delay(email=new_email, username=new_username)
                    cache.set(f"{self.user.pk}", new_email, timeout=300)
                    return redirect('accounts:activation', pk=self.user.pk)
