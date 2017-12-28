from django import forms
from django.contrib.auth import get_user_model

from .models import ContactUs

AuthUser = get_user_model()


class SignUpForm(forms.ModelForm):
    class Meta:
        model = AuthUser
        fields = ('email', 'password', )

    def save(self, commit=True):
        super(SignUpForm, self).save(commit=False)
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = AuthUser.objects.create_site_user(email, password)
        if commit:
            user.save()
        return user


class SignInForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, max_length=20)


class ContactUsForm(forms.ModelForm):
    class Meta:
        model = ContactUs
        fields = ('name', 'email', 'message', )


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    birthdate = forms.DateField()
    email = forms.EmailField()
    phone = forms.CharField()
    address = forms.CharField()
    postcode = forms.IntegerField()
