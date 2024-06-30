from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView
from accounts.forms import CustomSignUpForm, VerifyForm, CustomUserLoginForm
from accounts.models import User
from customers.models import Customer
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.core.cache import cache
from .tasks import otp_sender
from core.mixin import NavbarMixin
from orders.models import Order


class SignupView(NavbarMixin, CreateView):
    form_class = CustomSignUpForm
    template_name = 'account/signup.html'

    def form_valid(self, form):
        user = form.save(commit=True)
        otp_sender.delay(email=user.email, username=user.username)
        return redirect('accounts:activation', pk=user.pk)


class CustomUserLoginView(View):
    template_name = 'account/login.html'

    def get(self, request, *args, **kwargs):
        form = CustomUserLoginForm()
        return render(request, self.template_name, {'form': form, 'current_url': 'login'})

    def post(self, request, *args, **kwargs):
        form = CustomUserLoginForm(request.POST)
        # get next URL
        next_url = request.COOKIES.get('next_url')

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user and password:
                if user.is_active:
                    login(request, user)
                    # use next URL if exist then delete it
                    if next_url:
                        response = redirect(next_url)
                        response.delete_cookie('next_url')
                        return response

                    return redirect('products:home')
                else:
                    otp_sender.delay(email=user.email, username=user.username)
                    return redirect('accounts:activation', pk=user.pk)

            elif user:
                otp_sender.delay(email=user.email, username=user.username)
                return redirect('accounts:activation', pk=user.pk)

            else:
                form.add_error(None, 'Invalid email or password')
        return render(request, self.template_name, {'form': form, 'current_url': 'login'})


class UserActivationView(NavbarMixin, FormView):
    template_name = 'account/verification.html'
    form_class = VerifyForm

    def dispatch(self, request, *args, **kwargs):
        self.pk = self.kwargs['pk']
        self.new_user = get_object_or_404(User, pk=self.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        code = form.cleaned_data.get('code')
        self.new_user.backend = 'django.contrib.auth.backends.ModelBackend'

        # change email verification
        if cache.get(f"{self.pk}") and self.request.user.pk == self.pk:
            new_email = cache.get(f"{self.pk}")
            sent_code = cache.get(f"{new_email}")

            if code == str(sent_code):
                self.new_user.email = new_email
                self.new_user.save()
                cache.delete(f"{new_email}")
                cache.delete(f"{self.pk}")
                login(self.request, self.new_user)
                return redirect('customers:profile')

        # login and signup validation
        otp_model = cache.get(f"{self.new_user.email}")
        if otp_model:
            if code == str(otp_model):
                if not self.new_user.is_active:
                    self.new_user.is_active = True
                    self.new_user.save(update_fields=['is_active'])
                    customer = Customer.objects.create(customer=self.new_user)
                    Order.objects.create(customer=customer)

                cache.delete(f"{self.new_user.email}")
                login(self.request, self.new_user)

                # Check if next URL
                next_url = self.request.COOKIES.get('next_url')
                if next_url:
                    response = redirect(next_url)
                    response.delete_cookie('next_url')
                    return response

                return redirect('products:home')

        form.add_error(None, 'Invalid code or OTP expired.')
        return self.form_invalid(form)


class CustomUserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:login')
