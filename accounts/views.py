from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView
from accounts.forms import CustomSignUpForm, VerifyForm
from utils.otp import otp_sender
from accounts.models import User, OTPModel
from customers.models import Customer
from django.contrib.auth import authenticate, login, logout


class SignupView(CreateView):
    form_class = CustomSignUpForm
    template_name = 'account/signup.html'

    def form_valid(self, form):
        user = form.save(commit=True)
        otp_sender(user=user)
        return redirect('accounts:activation', pk=user.pk)


class UserActivationView(FormView):
    template_name = 'account/verification.html'
    form_class = VerifyForm

    def dispatch(self, request, *args, **kwargs):
        self.pk = self.kwargs['pk']
        self.new_user = get_object_or_404(User, pk=self.pk)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        code = form.cleaned_data.get('code')
        if code == str(OTPModel.objects.get(user=self.new_user).code):
            if not self.new_user.is_active:
                self.new_user.is_active = True
                self.new_user.save(update_fields=['is_active'])
                Customer.objects.create(customer=self.new_user)
                login(self.request, self.new_user)
                return render(self.request, 'test/test.html', context={'message': 'valid'})  ##todo:redirect to home
            login(self.request, self.new_user)
            return render(self.request,
                          'test/test.html',
                          context={'message': 'was activated'}
                          )  ## temporary todo:redirect to home
        else:
            form.add_error(None, 'Invalid code or OTP expired.')
            return self.form_invalid(form)
