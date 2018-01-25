from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import SiteUser

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


class ContactUsForm(forms.Form):
    name = forms.CharField(max_length=20)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)

    def contact_us(self):
        data = self.cleaned_data
        subject = settings.CONTACT_US_SUBJECT.format(name=data['name'])
        send_mail(subject, data['message'], data['email'], [settings.SITE_SETTINGS['contact_email']])


class ProfileForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    birthdate = forms.DateField(required=False)
    email = forms.EmailField()
    phone = forms.CharField(required=False)
    address = forms.CharField(required=False)
    postcode = forms.IntegerField(required=False)
    photo = forms.ImageField(required=False)

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
