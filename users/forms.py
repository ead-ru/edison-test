from django import forms
from django.contrib.auth import password_validation
from users import models


class UserRegisterForm(forms.ModelForm):
    ''' '''

    password1 = forms.CharField(strip=False)
    password2 = forms.CharField(strip=False)

    class Meta:
        model = models.User
        fields = ['email', ]

    def clean_password2(self):
        ''' '''
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError('Password mismatch')
            password_validation.validate_password(password2, self.instance)
        return password2

    def save(self, commit=True):
        ''' '''
        if self.cleaned_data['password2']:
            self.instance.set_password(self.cleaned_data['password2'])
        return super().save(commit)
