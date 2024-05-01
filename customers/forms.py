from django import forms
from accounts.models import User


class EditProfileForm(forms.ModelForm):
    name = forms.CharField(label='name', widget=forms.TextInput(), required=False)
    phone = forms.CharField(label='phone', widget=forms.TextInput(), required=False)

    class Meta:
        model = User
        fields = ['username', ]
