from django import forms
from django.contrib.auth import get_user_model
from academy_site.models import City, Partner, Teacher

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


class TeacherForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    photo = forms.ImageField()
    city = forms.ModelChoiceField(queryset=City.objects.all())
    facebook_link = forms.URLField(required=False)
    instagram_link = forms.URLField(required=False)
    other_link = forms.URLField(required=False)
    bio = forms.CharField(required=False, widget=forms.Textarea)

    def save(self, partner=None):
        data = self.cleaned_data
        auth_data = {
            'email': data.pop('email'),
            'password': data.pop('password'),
            'photo': data.pop('photo'),
            'city': data.pop('city'),
        }
        auth_teacher = AuthUser.objects.create_teacher(**auth_data)
        Teacher.objects.filter(auth_user=auth_teacher).update(**data)
