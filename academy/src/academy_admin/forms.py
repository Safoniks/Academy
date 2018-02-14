from django import forms
from django.contrib.auth import get_user_model
from academy_site.models import City, Partner, AdminProfile, Theme, Course
from academy_site.coices import *

AuthUser = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, max_length=20)


class CityForm(forms.Form):
    name = forms.CharField()
    short_description = forms.CharField(widget=forms.Textarea)
    full_description = forms.CharField(widget=forms.Textarea)
    location = forms.CharField()
    email = forms.EmailField()
    phone = forms.CharField()
    photo = forms.ImageField()

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
                })

    def save(self):
        data = self.cleaned_data
        if hasattr(self, 'city'):
            city = self.city
            for field in self.fields:
                setattr(city, field, data[field])
        else:
            city = City(**data)
        city.save()


class PartnerForm(forms.Form):
    name = forms.CharField()
    link = forms.URLField()
    logo = forms.ImageField()
    cities = forms.ModelMultipleChoiceField(
        queryset=City.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )

    def __init__(self, *args, **kwargs):
        partner = kwargs.pop('partner', None)
        super(PartnerForm, self).__init__(*args, **kwargs)
        if partner:
            self.partner = partner
            if not self.data:
                self.initial.update({
                    'name': partner.name,
                    'link': partner.link,
                    'logo': partner.logo,
                    'cities': partner.city_set.all(),
                })

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


class TeacherForm(forms.Form):
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

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super(TeacherForm, self).__init__(*args, **kwargs)
        if teacher:
            self.fields.pop('email', None)
            self.fields.pop('password', None)
            self.fields.pop('city', None)
            self.teacher = teacher
            if not self.data:
                self.initial.update({
                    'photo': teacher.auth_user.photo,
                    'first_name': teacher.auth_user.first_name,
                    'last_name': teacher.auth_user.last_name,
                    'is_city_admin': teacher.auth_user.is_superuser,
                    'facebook_link': teacher.facebook_link,
                    'instagram_link': teacher.instagram_link,
                    'other_link': teacher.other_link,
                    'bio': teacher.bio,
                })

    def save(self):
        data = self.cleaned_data
        is_city_admin = data.pop('is_city_admin')
        profile_data = {
            'facebook_link': data.pop('facebook_link'),
            'instagram_link': data.pop('instagram_link'),
            'other_link': data.pop('other_link'),
            'bio': data.pop('bio'),
        }
        if hasattr(self, 'teacher'):
            teacher = self.teacher
            for field in data:
                setattr(teacher.auth_user, field, data[field])
            teacher.auth_user.is_superuser = is_city_admin
            teacher.auth_user.save()
            # Teacher.objects.filter(pk=teacher.pk).update(**profile_data)
        else:
            AuthUser.objects.create_teacher(profile_data=profile_data, is_superuser=is_city_admin, **data)


class ThemeForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(required=False, widget=forms.Textarea)
    photo = forms.ImageField()
    city = forms.ModelChoiceField(queryset=City.objects.all())
    partners = forms.ModelMultipleChoiceField(
        queryset=Partner.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )

    def __init__(self, *args, **kwargs):
        theme = kwargs.pop('theme', None)
        super(ThemeForm, self).__init__(*args, **kwargs)
        if theme:
            self.fields.pop('name', None)
            self.fields.pop('city', None)
            self.fields['partners'].queryset = theme.city.partners.all()
            self.theme = theme
            if not self.data:
                self.initial.update({
                    'description': theme.description,
                    'photo': theme.photo,
                    'partners': theme.partners.all(),
                })
        else:
            self.fields.pop('partners', None)

    def save(self):
        data = self.cleaned_data
        if hasattr(self, 'theme'):
            theme = self.theme
            partners = data.pop('partners', [])
            for field in data:
                setattr(theme, field, data[field])
            theme.partners.clear()
            theme.partners.add(*partners)
        else:
            theme = Theme(**data)
        theme.save()


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
    # teachers = forms.ModelMultipleChoiceField(
    #     queryset=Teacher.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    # )
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


class SecurityForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    photo = forms.ImageField()
    city = forms.ModelChoiceField(queryset=City.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        admin = kwargs.pop('admin', None)
        super(SecurityForm, self).__init__(*args, **kwargs)
        if admin:
            # if admin.get_role() == TEACHER_CITY_ADMIN:
            #     self.fields['is_city_admin'] = forms.BooleanField(required=False)
            #     self.initial['is_city_admin'] = admin.is_superuser
            self.admin = admin
            self.fields.pop('email', None)
            self.fields.pop('password', None)
            self.fields.pop('city', None)
            if not self.data:
                self.initial.update({
                    'first_name': admin.first_name,
                    'last_name': admin.last_name,
                    'photo': admin.photo,
                })

    def save(self):
        data = self.cleaned_data
        if hasattr(self, 'admin'):
            admin = self.admin
            is_city_admin = data.pop('is_city_admin', None)
            for field in data:
                setattr(admin, field, data[field])
            if not (is_city_admin is None):
                admin.is_superuser = is_city_admin
            admin.save()
        else:
            AuthUser.objects.create_admin(**data)
