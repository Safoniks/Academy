from django import forms
from django.contrib.auth import get_user_model

from .models import ContactUs, SiteUser

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
    first_name = forms.CharField()
    last_name = forms.CharField()
    birthdate = forms.DateField()
    email = forms.EmailField()
    phone = forms.CharField()
    address = forms.CharField()
    postcode = forms.IntegerField()
    photo = forms.ImageField()

    # def clean(self):
    #     form_data = self.cleaned_data
    #     if form_data['password'] != form_data['password_repeat']:
    #         self._errors["password"] = ["Password do not match"]  # Will raise a error message
    #         del form_data['password']
    #     return form_data

    def save(self, auth_user):
        data = self.cleaned_data
        auth_user.email = data.pop('email')
        auth_user.first_name = data.pop('first_name')
        auth_user.last_name = data.pop('last_name')
        auth_user.photo = data.pop('photo')
        auth_user.save()

        SiteUser.objects.filter(auth_user=auth_user).update(**data)
