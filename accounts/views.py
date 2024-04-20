from django.shortcuts import render, redirect
from django.views.generic import CreateView
from accounts.forms import CustomSignUpForm
from utils.otp import otp_sender


class SignupView(CreateView):
    form_class = CustomSignUpForm
    template_name = 'account/signup.html'

    def form_valid(self, form):
        user = form.save(commit=True)
        otp_sender(user=user)
        return render(self.request, 'test/test.html')
