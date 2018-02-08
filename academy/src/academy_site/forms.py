from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import SiteUser, UserCourse

AuthUser = get_user_model()


class SignUpForm(forms.ModelForm):
    class Meta:
        model = AuthUser
        fields = ('email', 'password',)

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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        if user:
            self.user = user
            if not self.data:
                self.initial.update({
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'photo': user.photo,
                    'birthdate': user.siteuser.birthdate,
                    'phone': user.siteuser.phone,
                    'address': user.siteuser.address,
                    'postcode': user.siteuser.postcode,
                })

    # def clean(self):
    #     form_data = self.cleaned_data
    #     if form_data['password'] != form_data['password_repeat']:
    #         self._errors["password"] = ["Password do not match"]  # Will raise a error message
    #         del form_data['password']
    #     return form_data

    def save(self):
        data = self.cleaned_data
        auth_user = self.user
        auth_data = {
            'email': data.pop('email'),
            'first_name': data.pop('first_name'),
            'last_name': data.pop('last_name'),
            'photo': data.pop('photo'),
        }
        for field in auth_data:
            setattr(auth_user, field, auth_data[field])
        auth_user.save()

        SiteUser.objects.filter(auth_user=auth_user).update(**data)


class SignUpCourseForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    birthdate = forms.DateField()
    email = forms.EmailField()
    phone = forms.CharField()
    address = forms.CharField()
    postcode = forms.IntegerField()
    photo = forms.ImageField()
    know_academy_through = forms.CharField()
    questions = forms.CharField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(SignUpCourseForm, self).__init__(*args, **kwargs)
        if user:
            self.user = user
            if not self.data:
                self.initial.update({
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'photo': user.photo,
                    'birthdate': user.siteuser.birthdate,
                    'phone': user.siteuser.phone,
                    'address': user.siteuser.address,
                    'postcode': user.siteuser.postcode,
                })

    def save(self, course):
        data = self.cleaned_data
        auth_user = self.user
        know_academy_through = data.pop('know_academy_through')
        questions = data.pop('questions')
        auth_data = {
            'email': data.pop('email'),
            'first_name': data.pop('first_name'),
            'last_name': data.pop('last_name'),
            'photo': data.pop('photo'),
        }

        for field in auth_data:
            setattr(auth_user, field, auth_data[field])
        auth_user.save()

        SiteUser.objects.filter(auth_user=auth_user).update(**data)
        UserCourse(
            user=auth_user.siteuser,
            course=course,
            know_academy_through=know_academy_through,
            questions=questions
        ).save()
