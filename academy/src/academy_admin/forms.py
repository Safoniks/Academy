from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from academy_site.models import City, Partner, AdminProfile, Theme, Course
from academy_site.choices import *

AuthUser = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, max_length=20)


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


class CityForm(forms.Form):
    name = forms.CharField()
    short_description = forms.CharField(widget=forms.Textarea)
    full_description = forms.CharField(widget=forms.Textarea)
    location = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    photo = forms.ImageField(required=False)
    video = forms.URLField(required=False)

    def __init__(self, *args, **kwargs):
        city = kwargs.pop('city', None)
        super(CityForm, self).__init__(*args, **kwargs)
        if city:
            self.fields.pop('name', None)
            self.city = city
            if not self.data:
                self.initial.update({
                    'short_description': city.short_description,
                    'full_description': city.full_description,
                    'location': city.location,
                    'email': city.email,
                    'phone': city.phone,
                    'photo': city.photo,
                    'video': city.video,
                })

    def clean(self):
        form_data = self.cleaned_data
        photo = form_data.get('photo', None)
        video = form_data.get('video', None)

        if (photo and video) or (not photo and not video):
            self._errors["photo"] = ["PHOTO OR VIDEO"]
            self._errors["video"] = ["PHOTO OR VIDEO"]

        return form_data

    def save(self):
        data = self.cleaned_data
        if hasattr(self, 'city'):
            city = self.city
            for field in self.fields:
                setattr(city, field, data[field])
        else:
            city = City(**data)
        city.save()


class ThemeForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    photo = forms.ImageField()
    city = forms.ModelChoiceField(queryset=City.objects.all())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        selected_city = kwargs.pop('city', None)
        theme = kwargs.pop('theme', None)
        super(ThemeForm, self).__init__(*args, **kwargs)
        self.user = user
        if theme:
            self.fields.pop('name', None)
            self.fields.pop('city', None)
            self.theme = theme
            if not self.data:
                self.initial.update({
                    'description': theme.description,
                    'photo': theme.photo,
                })
        else:
            if selected_city:
                self.fields['city'].initial = selected_city
            if user.is_moderator:
                self.fields['city'].widget = forms.HiddenInput()
                self.fields['city'].initial = user.city

    def clean_city(self):
        city = self.cleaned_data['city']
        user = self.user
        if user.is_moderator and user.city != city:
            raise ValidationError("Moderator can not create a theme in another city.")
        return city

    def save(self):
        data = self.cleaned_data
        if hasattr(self, 'theme'):
            theme = self.theme
            for field in data:
                setattr(theme, field, data[field])
        else:
            theme = Theme(**data)
        theme.save()


class CourseForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    photo = forms.ImageField()
    location = forms.CharField()
    practise_info = forms.CharField(widget=forms.Textarea)
    price = forms.DecimalField(decimal_places=2, max_digits=10)
    price_description = forms.CharField(widget=forms.Textarea)
    seats = forms.IntegerField()
    theme = forms.ModelChoiceField(queryset=Theme.objects.all())
    teachers = forms.ModelMultipleChoiceField(
        queryset=AuthUser.objects.teachers(), widget=forms.CheckboxSelectMultiple, required=False
    )
    partners = forms.ModelMultipleChoiceField(
        queryset=Partner.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )

    def __init__(self, *args, **kwargs):
        themes = kwargs.pop('themes', None)
        teachers = kwargs.pop('teachers', None)
        partners = kwargs.pop('partners', None)
        selected_theme = kwargs.pop('selected_theme', None)
        super(CourseForm, self).__init__(*args, **kwargs)
        if themes:
            self.fields['theme'].queryset = themes
            if selected_theme:
                self.fields['theme'].initial = selected_theme
        if teachers:
            self.fields['teachers'].queryset = teachers
        if partners:
            self.fields['partners'].queryset = partners

    def save(self):
        data = self.cleaned_data
        if 'save_draft' in self.data:
            data['status'] = PLANNED
        else:
            data['status'] = AVAILABLE
        teachers = data.pop('teachers', [])
        partners = data.pop('partners', [])
        course = Course(**data)
        course.save()
        course.teachers.add(*teachers)
        course.partners.add(*partners)


class PartnerForm(forms.Form):
    name = forms.CharField()
    link = forms.URLField()
    logo = forms.ImageField()
    is_general = forms.BooleanField(required=False)
    cities = forms.ModelMultipleChoiceField(
        queryset=City.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        selected_city = kwargs.pop('city', None)
        partner = kwargs.pop('partner', None)
        super(PartnerForm, self).__init__(*args, **kwargs)
        self.user = user
        if user.is_moderator:
            self.fields['is_general'].widget = forms.HiddenInput()
            self.fields['is_general'].required = False
            self.fields['cities'].widget = forms.MultipleHiddenInput()
        if partner:
            self.partner = partner
            if not self.data:
                self.initial.update({
                    'name': partner.name,
                    'link': partner.link,
                    'logo': partner.logo,
                    'is_general': partner.is_general,
                    'cities': partner.city_set.all(),
                })
        else:
            if selected_city:
                self.fields['cities'].initial = (selected_city.pk, )
            if user.is_moderator:
                self.fields['is_general'].initial = False
                self.fields['cities'].initial = (user.city.pk, )

    def clean_cities(self):
        cities = self.cleaned_data['cities']
        user = self.user
        if user.is_moderator and user.city not in cities:
            raise ValidationError("Moderator can not create a partner in another city.")
        return cities

    def save(self):
        data = self.cleaned_data
        cities = data.pop('cities', [])
        if hasattr(self, 'partner'):
            partner = self.partner
            for field in data:
                setattr(partner, field, data[field])
        else:
            partner = Partner(**data)
        partner.save()
        partner.city_set.clear()
        partner.city_set.add(*cities)


class CreateBackOfficeUserForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    city = forms.ModelChoiceField(queryset=City.objects.all())
    photo = forms.ImageField(required=False)
    phone = forms.CharField(required=False)
    facebook_link = forms.URLField(required=False)
    instagram_link = forms.URLField(required=False)
    other_link = forms.URLField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    role = forms.ChoiceField(choices=ADMIN_ROLE_CHOICES, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        selected_city = kwargs.pop('city', None)
        super(CreateBackOfficeUserForm, self).__init__(*args, **kwargs)
        self.request = request
        if request.resolver_match.url_name == 'add_teacher':
            self.fields.pop('role', None)
        if selected_city:
            self.fields['city'].initial = selected_city
        if request.user.is_moderator:
            self.fields['city'].widget = forms.HiddenInput()
            self.fields['city'].initial = request.user.city

    def clean_city(self):
        city = self.cleaned_data['city']
        user = self.request.user
        if user.is_moderator and user.city != city:
            raise ValidationError("Moderator can not create a teacher in another city.")
        return city

    def save(self):
        request = self.request
        data = self.cleaned_data
        role = data.pop('role', TEACHER)
        profile_data = {
            'phone': data.pop('phone', None),
            'facebook_link': data.pop('facebook_link', None),
            'instagram_link': data.pop('instagram_link', None),
            'other_link': data.pop('other_link', None),
            'bio': data.pop('bio', None),
        }
        if request.resolver_match.url_name == 'add_teacher':
            AuthUser.objects.create_teacher(profile_data=profile_data, **data)
        else:
            if role == ADMINISTRATOR:
                AuthUser.objects.create_admin(profile_data=profile_data, **data)
            if role == MODERATOR:
                AuthUser.objects.create_moderator(profile_data=profile_data, **data)


class EditBackOfficeUserForm(forms.Form):
    city = forms.ModelChoiceField(queryset=City.objects.all())
    role = forms.ChoiceField(choices=BACKOFFICE_ROLE_CHOICES, widget=forms.RadioSelect())

    def __init__(self, *args, **kwargs):
        back_office_user = kwargs.pop('back_office_user', None)
        super(EditBackOfficeUserForm, self).__init__(*args, **kwargs)
        self.back_office_user = back_office_user
        self.fields['city'].initial = back_office_user.city
        self.fields['role'].initial = back_office_user.get_role()

    def save(self):
        back_office_user = self.back_office_user
        data = self.cleaned_data
        role = data.pop('role')
        city = data.pop('city')
        back_office_user.city = city
        back_office_user.set_role(role)
        back_office_user.save()
        back_office_user.adminprofile.save()


class ProfileForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    city = forms.ModelChoiceField(queryset=City.objects.all())
    photo = forms.ImageField(required=False)
    phone = forms.CharField(required=False)
    facebook_link = forms.URLField(required=False)
    instagram_link = forms.URLField(required=False)
    other_link = forms.URLField(required=False)
    bio = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)

        if user:
            self.user = user
            if not user.is_administrator:
                self.fields.pop('city', None)
            if not self.data:
                self.initial.update({
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'photo': user.photo,
                    'phone': user.adminprofile.phone,
                    'facebook_link': user.adminprofile.facebook_link,
                    'instagram_link': user.adminprofile.instagram_link,
                    'other_link': user.adminprofile.other_link,
                    'bio': user.adminprofile.bio,
                })
                if user.is_administrator:
                    self.initial.update({
                        'city': user.city,
                    })

    def save(self):
        data = self.cleaned_data
        auth_user = self.user
        city = data.pop('city', None)
        auth_data = {
            'email': data.pop('email'),
            'first_name': data.pop('first_name'),
            'last_name': data.pop('last_name'),
            'photo': data.pop('photo'),
        }
        city and auth_data.update({'city': city})
        for field in auth_data:
            setattr(auth_user, field, auth_data[field])
        auth_user.save()

        data['last_update'] = timezone.now()
        AdminProfile.objects.filter(auth_user=auth_user).update(**data)
