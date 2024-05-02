from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password


class EditProfileForm(forms.Form):
    name = forms.CharField(label='name', widget=forms.TextInput(), required=False)
    phone = forms.CharField(label='phone', widget=forms.TextInput(), required=False)
    email = forms.EmailField(label='phone', widget=forms.TextInput())
    username = forms.CharField(label='phone', widget=forms.TextInput())


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password1 = forms.CharField(widget=forms.PasswordInput())
    new_password2 = forms.CharField(widget=forms.PasswordInput())

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not check_password(old_password, self.user.password):
            raise forms.ValidationError("Your old password was entered incorrectly. Please enter it again.")
        return old_password

    def clean_password1(self):
        return self.cleaned_data.get('new_password1')

    def clean_password2(self):
        return self.cleaned_data.get('new_password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["new_password1"])
        if commit:
            user.save()
        return user
