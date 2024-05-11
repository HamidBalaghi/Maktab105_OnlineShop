from django import forms
from orders.models import DiscountCode


class CheckoutForm(forms.Form):
    address = forms.ChoiceField(label='Select an address', choices=[], required=True)
    discount_code = forms.CharField(label='Enter Discount Code', max_length=100, required=False)

    def clean_discount_code(self):
        discount_code = self.cleaned_data.get('discount_code')
        if discount_code:
            if not DiscountCode.objects.filter(code=discount_code, is_deleted=False, is_used=False).exists():
                raise forms.ValidationError("Invalid discount code.")
        return discount_code
