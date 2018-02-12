from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils import timezone

from utils import generate_confirmation_code, send_reset_password_email

from .models import SiteUser, UserCourse

AuthUser = get_user_model()


class SignUpForm(forms.ModelForm):
    class Meta:
        model = AuthUser
        fields = ('first_name', 'last_name', 'email', 'password',)

    def save(self, commit=True):
        data = self.cleaned_data
        profile_data = {
            'confirmation_code': generate_confirmation_code(data['email']),
            'confirmation_code_expires': timezone.now() + settings.SIGNUP_CONFIRMATION_CODE_EXPIRE,
        }
        user = AuthUser.objects.create_site_user(profile_data=profile_data, **data)
        if commit:
            user.save()
        return user


class SignInForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, max_length=20)


class ResetPasswordForm(forms.Form):
    email = forms.EmailField()

    def clean(self):
        form_data = self.cleaned_data
        email = form_data['email']
        user = AuthUser.objects.filter(email=email).first()
        if not user:
            self._errors["email"] = ["User does not exist."]
            del form_data['email']
        form_data['user'] = user
        return form_data

    def send_email(self):
        user = self.cleaned_data['user']
        new_password = AuthUser.objects.make_random_password()
        user.set_password(new_password)
        user.save()
        send_reset_password_email(user, new_password)


class ChangePassword(forms.Form):
    old_password = forms.CharField()
    new_password = forms.CharField()
    reenter_password = forms.CharField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ChangePassword, self).__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        form_data = self.cleaned_data
        old_password = form_data.get('old_password')
        new_password = form_data.get('new_password')
        reenter_password = form_data.get('reenter_password')

        if new_password and new_password != reenter_password or new_password == old_password:
            self._errors["new_password"] = ["Invalid password"]
            del form_data['new_password']
            del form_data['reenter_password']
        if not self.user.check_password(old_password):
            self._errors["old_password"] = ["Wrong password"]
            del form_data['old_password']
        return form_data

    def save(self):
        user = self.user
        user.set_password(self.cleaned_data['new_password'])
        user.save()


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
    country = forms.CharField(required=False)
    city = forms.CharField(required=False)
    address = forms.CharField(required=False)
    postcode = forms.IntegerField(required=False)
    photo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
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
                    'country': user.siteuser.country,
                    'city': user.siteuser.city,
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
    country = forms.CharField()
    city = forms.CharField()
    address = forms.CharField()
    postcode = forms.IntegerField()
    photo = forms.ImageField()
    mother_language = forms.CharField()
    know_academy_through = forms.CharField()
    questions = forms.CharField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        course = kwargs.pop('course', None)
        super(SignUpCourseForm, self).__init__(*args, **kwargs)
        self.course = course
        if getattr(user, 'is_authenticated', False):
            self.fields['email'].widget.attrs['readonly'] = True
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

    def clean(self):
        form_data = self.cleaned_data
        email = form_data['email']
        if UserCourse.objects.filter(user__auth_user__email=email, course=self.course).exists():
            self._errors["email"] = ["Already signed up with this email."]
            del form_data['email']
        if not isinstance(self.user, AuthUser):
            try:
                self.user = AuthUser.objects.get(email=email)
            except ObjectDoesNotExist:
                pass
        return form_data

    def save(self):
        data = self.cleaned_data
        auth_user = self.user
        if 'signup_and_create' in self.data and not auth_user.is_active:
            pass
        mother_language = data.pop('mother_language')
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
            course=self.course,
            mother_language=mother_language,
            know_academy_through=know_academy_through,
            questions=questions
        ).save()
