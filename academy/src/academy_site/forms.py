from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.utils import timezone
from django.db.models import Q

from utils import generate_confirmation_code, send_reset_password_email

from .models import SiteUser, UserCourse, Anonymous

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
    email_to = forms.EmailField(widget=forms.HiddenInput(), required=False)
    message = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        email_to = kwargs.pop('email_to', None)
        super(ContactUsForm, self).__init__(*args, **kwargs)
        self.fields['email_to'].initial = email_to

    def contact_us(self):
        data = self.cleaned_data
        email_to = data.pop('email_to')
        subject = settings.CONTACT_US_SUBJECT.format(name=data['name'])
        send_mail(subject, data['message'], data['email'], [email_to])


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
    mother_language = forms.CharField(required=False)
    salutation = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.user = user
        self.fields['email'].widget.attrs['readonly'] = True
        if user:
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
                'mother_language': user.siteuser.mother_language,
                'salutation': user.siteuser.salutation,
            })

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
    mother_language = forms.CharField()
    salutation = forms.CharField()
    know_academy_through = forms.CharField()
    questions = forms.CharField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        course = kwargs.pop('course', None)
        super(SignUpCourseForm, self).__init__(*args, **kwargs)
        self.user = user
        self.course = course
        if getattr(user, 'is_authenticated', False):
            self.fields['email'].widget.attrs['readonly'] = True
            if user.siteuser.know_academy_through:
                self.fields.pop('know_academy_through')
            self.initial.update({
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'birthdate': user.siteuser.birthdate,
                'phone': user.siteuser.phone,
                'country': user.siteuser.country,
                'city': user.siteuser.city,
                'address': user.siteuser.address,
                'postcode': user.siteuser.postcode,
                'mother_language': user.siteuser.mother_language,
                'salutation': user.siteuser.salutation,
            })
        else:
            self.fields['password'] = forms.CharField(max_length=20, required=False)  # Тимчасово

    def clean(self):
        form_data = self.cleaned_data
        email = form_data['email']

        if 'signup_and_create' in self.data and not self.user.is_authenticated and not form_data.get('password',
                                                                                                     None):  # Тимчасово
            self._errors["password"] = ["For registration you need a password."]

        if UserCourse.objects.filter(
                        (Q(user__auth_user__email=email) | Q(anonymous__email=email)) & Q(course=self.course)
                        & (Q(is_confirmed=True) | Q(confirmation_code_expires__gt=timezone.now()))
                        & Q(is_unsubscribed=False)
        ).exists():
            self._errors["email"] = ["Already signed up with this email."]
            del form_data['email']
        return form_data

    def save(self):
        data = self.cleaned_data
        auth_user = self.user
        questions = data.pop('questions')
        email = data.pop('email')
        password = data.pop('password', None)
        auth_data = {
            'email': email,
            'first_name': data.pop('first_name'),
            'last_name': data.pop('last_name'),
        }
        confirmation_data = {
            'confirmation_code': generate_confirmation_code(email),
            'confirmation_code_expires': timezone.now() + settings.SIGNUP_COURSE_CONFIRMATION_CODE_EXPIRE,
        }
        if not auth_user.is_authenticated:
            if 'signup_and_create' in self.data:
                auth_data['password'] = password
                data.update(confirmation_data)
                new_user = AuthUser.objects.create_site_user(profile_data=data, **auth_data)
                new_user.save()

                user_course = UserCourse(
                    user=new_user.siteuser,
                    course=self.course,
                    questions=questions,
                    **confirmation_data
                )
                user_course.save()
                return user_course
            else:
                data = {**data, **auth_data}
                user_course = UserCourse.objects.filter(course=self.course, anonymous__email=email).first()
                if user_course:
                    Anonymous.objects.filter(pk=user_course.anonymous.pk).update(**data)
                    user_course.questions = questions
                    user_course.date = timezone.now()
                    user_course.confirmation_code = confirmation_data['confirmation_code']
                    user_course.confirmation_code_expires = confirmation_data['confirmation_code_expires']
                    user_course.is_unsubscribed = False
                    user_course.count += 1
                    user_course.save()
                    return user_course
                else:
                    anonymous = Anonymous(**data)
                    anonymous.save()

                    user_course = UserCourse(
                        anonymous=anonymous,
                        course=self.course,
                        questions=questions,
                        **confirmation_data
                    )
                    user_course.save()
                    return user_course

        for field in auth_data:
            setattr(auth_user, field, auth_data[field])
        auth_user.save()
        SiteUser.objects.filter(auth_user=auth_user).update(**data)

        user_course = UserCourse.objects.filter(course=self.course, user__auth_user__email=email).first()
        if user_course:
            user_course.questions = questions
            user_course.date = timezone.now()
            user_course.confirmation_code = confirmation_data['confirmation_code']
            user_course.confirmation_code_expires = confirmation_data['confirmation_code_expires']
            user_course.is_unsubscribed = False
            user_course.count += 1
            user_course.save()
            return user_course
        else:
            user_course = UserCourse(
                user=auth_user.siteuser,
                course=self.course,
                questions=questions,
                is_confirmed=auth_user.siteuser.is_confirmed,
                **confirmation_data
            )
            user_course.save()
            return user_course
