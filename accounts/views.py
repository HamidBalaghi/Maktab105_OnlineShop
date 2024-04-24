from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView
from accounts.forms import CustomSignUpForm, VerifyForm, CustomUserLoginForm
from utils.otp import otp_sender, is_otp_expired
from accounts.models import User, OTPModel
from customers.models import Customer
from django.contrib.auth import authenticate, login, logout
from django.views import View


class SignupView(CreateView):
    form_class = CustomSignUpForm
    template_name = 'account/signup.html'

    def form_valid(self, form):
        user = form.save(commit=True)
        otp_sender(user=user)
        return redirect('accounts:activation', pk=user.pk)


class CustomUserLoginView(View):
    template_name = 'account/login.html'

    def get(self, request, *args, **kwargs):
        form = CustomUserLoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user and password:
                if user.is_active:
                    login(request, user)
                    return redirect('products:home')
                else:
                    otp_sender(user)
                    return redirect('accounts:activation', pk=user.pk)

            elif user:
                otp_sender(user)
                return redirect('accounts:activation', pk=user.pk)
            else:
                form.add_error(None, 'Invalid email or password')
        return render(request, self.template_name, {'form': form})


class UserActivationView(FormView):
    template_name = 'account/verification.html'
    form_class = VerifyForm

    def dispatch(self, request, *args, **kwargs):
        self.pk = self.kwargs['pk']
        self.new_user = get_object_or_404(User, pk=self.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        code = form.cleaned_data.get('code')
        self.new_user.backend = 'django.contrib.auth.backends.ModelBackend'
        otp_model = OTPModel.objects.get(user=self.new_user)
        if code == str(otp_model.code) and not is_otp_expired(otp_model):
            if not self.new_user.is_active:
                self.new_user.is_active = True
                self.new_user.save(update_fields=['is_active'])
                Customer.objects.create(customer=self.new_user)
                login(self.request, self.new_user)
                return redirect('products:home')
            login(self.request, self.new_user)
            return redirect('products:home')
        else:
            form.add_error(None, 'Invalid code or OTP expired.')
            return self.form_invalid(form)


class CustomUserLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:login')
