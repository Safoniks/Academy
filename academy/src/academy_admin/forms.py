from django import forms
from django.contrib.auth import get_user_model
from academy_site.models import City, Partner, Teacher, Theme, Course
from academy_site.coices import *

AuthUser = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, max_length=20)


class AddCityForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    school_address = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    photo = forms.ImageField()

    def save(self):
        data = self.cleaned_data
        City(**data).save()


class UpdateCityForm(forms.Form):
    description = forms.CharField(widget=forms.Textarea)
    school_address = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    photo = forms.ImageField()

    def save(self, city):
        data = self.cleaned_data
        city.description = data['description']
        city.school_address = data['school_address']
        city.email = data['email']
        city.phone = data['phone']
        city.photo = data['photo']
        city.save()


class PartnerForm(forms.Form):
    name = forms.CharField()
    link = forms.URLField()
    logo = forms.ImageField()
    cities = forms.ModelMultipleChoiceField(
        queryset=City.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )

    def save(self, partner=None):
        data = self.cleaned_data
        cities = data.pop('cities', [])
        if partner:
            partner.name = data['name']
            partner.link = data['link']
            partner.logo = data['logo']
        else:
            partner = Partner(**data)
        partner.save()

        partner.city_set.clear()
        partner.city_set.add(*cities)


class AddTeacherForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    photo = forms.ImageField()
    city = forms.ModelChoiceField(queryset=City.objects.all())
    is_city_admin = forms.BooleanField(required=False)
    facebook_link = forms.URLField(required=False)
    instagram_link = forms.URLField(required=False)
    other_link = forms.URLField(required=False)
    bio = forms.CharField(required=False, widget=forms.Textarea)

    def save(self):
        data = self.cleaned_data
        is_city_admin = data.pop('is_city_admin')
        auth_data = {
            'email': data.pop('email'),
            'password': data.pop('password'),
            'photo': data.pop('photo'),
            'first_name': data.pop('first_name'),
            'last_name': data.pop('last_name'),
            'city': data.pop('city'),
        }
        AuthUser.objects.create_teacher(profile_data=data, is_superuser=is_city_admin, **auth_data)


class UpdateTeacherForm(forms.Form):
    photo = forms.ImageField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    is_city_admin = forms.BooleanField(required=False)
    facebook_link = forms.URLField(required=False)
    instagram_link = forms.URLField(required=False)
    other_link = forms.URLField(required=False)
    bio = forms.CharField(required=False, widget=forms.Textarea)

    def save(self, teacher):
        data = self.cleaned_data
        teacher.auth_user.photo = data.pop('photo')
        teacher.auth_user.first_name = data.pop('first_name')
        teacher.auth_user.last_name = data.pop('last_name')
        teacher.auth_user.is_superuser = data.pop('is_city_admin')
        teacher.auth_user.save()
        Teacher.objects.filter(pk=teacher.pk).update(**data)


class AddThemeForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(required=False, widget=forms.Textarea)
    photo = forms.ImageField()
    city = forms.ModelChoiceField(queryset=City.objects.all())

    def save(self):
        data = self.cleaned_data
        Theme(**data).save()


class UpdateThemeForm(forms.Form):
    description = forms.CharField(required=False, widget=forms.Textarea)
    photo = forms.ImageField()
    partners = forms.ModelMultipleChoiceField(
        queryset=Partner.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )

    def __init__(self, *args, **kwargs):
        partners = kwargs.pop('partners', None)
        super(UpdateThemeForm, self).__init__(*args, **kwargs)
        if partners:
            self.fields['partners'].queryset = partners

    def save(self, theme=None):
        data = self.cleaned_data
        partners = data.pop('partners', [])
        if theme:
            theme.description = data['description']
            theme.photo = data['photo']
            theme.save()
            theme.partners.clear()
            theme.partners.add(*partners)


class AddCourseForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    photo = forms.ImageField()
    location = forms.CharField()
    practise_info = forms.CharField(widget=forms.Textarea)
    price = forms.DecimalField(decimal_places=2, max_digits=10)
    price_description = forms.CharField(widget=forms.Textarea)
    seats = forms.IntegerField()
    status = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select())
    theme = forms.ModelChoiceField(queryset=Theme.objects.all())
    teachers = forms.ModelMultipleChoiceField(
        queryset=Teacher.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )
    partners = forms.ModelMultipleChoiceField(
        queryset=Partner.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )

    def __init__(self, *args, **kwargs):
        themes = kwargs.pop('themes', None)
        teachers = kwargs.pop('teachers', None)
        partners = kwargs.pop('partners', None)
        super(AddCourseForm, self).__init__(*args, **kwargs)
        if themes:
            self.fields['theme'].queryset = themes
        if teachers:
            self.fields['teachers'].queryset = teachers
        if partners:
            self.fields['partners'].queryset = partners

    def save(self):
        data = self.cleaned_data
        teachers = data.pop('teachers', [])
        partners = data.pop('partners', [])
        course = Course(**data)
        course.save()
        course.teachers.add(*teachers)
        course.partners.add(*partners)


class AddSecurityForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    photo = forms.ImageField()
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False)

    def save(self):
        data = self.cleaned_data
        AuthUser.objects.create_admin(**data)


class UpdateSecurityForm(forms.Form):
    first_name = forms.CharField()
    last_name = forms.CharField()
    photo = forms.ImageField()

    def __init__(self, *args, **kwargs):
        admin = kwargs.pop('admin', None)
        super(UpdateSecurityForm, self).__init__(*args, **kwargs)
        if admin.get_role() == TEACHER_CITY_ADMIN:
            self.fields['is_city_admin'] = forms.BooleanField(required=False)
            self.initial['is_city_admin'] = admin.is_superuser

    def save(self, admin):
        data = self.cleaned_data
        is_city_admin = data.pop('is_city_admin', None)
        if not (is_city_admin is None):
            admin.is_superuser = is_city_admin
        admin.photo = data.pop('photo')
        admin.first_name = data.pop('first_name')
        admin.last_name = data.pop('last_name')
        admin.save()
