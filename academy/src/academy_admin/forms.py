from django import forms
from academy_site.models import City, Partner


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
        if not partner:
            partner = Partner(**data)
            partner.save()
        partner.city_set.clear()
        partner.city_set.add(*cities)
