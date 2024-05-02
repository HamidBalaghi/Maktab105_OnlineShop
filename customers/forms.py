from django import forms


class EditProfileForm(forms.Form):
    name = forms.CharField(label='name', widget=forms.TextInput(), required=False)
    phone = forms.CharField(label='phone', widget=forms.TextInput(), required=False)
    email = forms.EmailField(label='phone', widget=forms.TextInput())
    username = forms.CharField(label='phone', widget=forms.TextInput())
