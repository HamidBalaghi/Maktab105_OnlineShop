from django.urls import reverse_lazy
from django.views.generic import UpdateView
from .forms import EditProfileForm
from .models import Customer
from accounts.models import User


class EditProfileView(UpdateView):
    model = User
    form_class = EditProfileForm
    template_name = 'customers/editprofile.html'
    success_url = reverse_lazy('products:home')

    def get_object(self, queryset=None):
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        customer = Customer.objects.get(customer=self.request.user)
        if customer:
            initial['name'] = customer.full_name
            initial['phone'] = customer.phone_number
        return initial

    def form_valid(self, form):
        user = form.save(commit=False)
        customer = Customer.objects.get(customer=self.get_object())
        customer.full_name = form.cleaned_data['name']
        customer.phone_number = form.cleaned_data['phone']
        customer.save()

        return super().form_valid(form)
