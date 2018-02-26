from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
from academy_site.models import City, Partner, AdminProfile, Theme, Course, Lesson
from academy_site.choices import *

AuthUser = get_user_model()


class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, max_length=20)


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField()
    new_password = forms.CharField()
    reenter_password = forms.CharField()

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
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
        self.city = city
        if city:
            self.fields.pop('name', None)
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

    def clean_video(self):
        video = self.cleaned_data['video']
        if not video.startswith('https://www.youtube.com/embed/'):
            raise ValidationError("Invalid video url.")
        return video

    def save(self):
        data = self.cleaned_data
        city = self.city
        if city:
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
        self.theme = theme
        if theme:
            self.fields.pop('name', None)
            self.fields.pop('city', None)
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
        theme = self.theme
        if theme:
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
        course = kwargs.pop('course', None)
        themes = kwargs.pop('themes', None)
        teachers = kwargs.pop('teachers', None)
        partners = kwargs.pop('partners', None)
        selected_theme = kwargs.pop('selected_theme', None)
        super(CourseForm, self).__init__(*args, **kwargs)
        self.course, self.themes, self.teachers, self.partners = course, themes, teachers, partners
        if course:
            self.fields['status'] = forms.ChoiceField(choices=STATUS_CHOICES, widget=forms.Select())
            self.initial.update({
                'status': course.status,
                'name': course.name,
                'description': course.description,
                'photo': course.photo,
                'location': course.location,
                'practise_info': course.practise_info,
                'price': course.price,
                'price_description': course.price_description,
                'seats': course.seats,
                'theme': course.theme,
                'teachers': course.teachers.all(),
                'partners': course.partners.all(),
            })
        self.fields['theme'].queryset = themes
        if selected_theme:
            self.fields['theme'].initial = selected_theme
        self.fields['teachers'].queryset = teachers
        self.fields['partners'].queryset = partners

    def clean_theme(self):
        theme = self.cleaned_data['theme']
        themes = self.themes
        if theme not in themes:
            raise ValidationError('Need a theme from the same city.')
        return theme

    def clean_teachers(self):
        teachers = self.cleaned_data['teachers']
        for teacher in teachers:
            if teacher not in self.teachers:
                raise ValidationError('Need a teacher from the same city.')
        return teachers

    def clean_partners(self):
        partners = self.cleaned_data['partners']
        for partner in partners:
            if partner not in self.partners:
                raise ValidationError('Need a partner from the same city.')
        return partners

    def clean_seats(self):
        seats = self.cleaned_data['seats']
        course = self.course
        if course and course.reserved_seats > seats:
            raise ValidationError('Already booked %d seats.' % course.reserved_seats)
        return seats

    def save(self):
        data = self.cleaned_data
        course = self.course
        teachers = data.pop('teachers', [])
        partners = data.pop('partners', [])
        if course:
            for field in data:
                setattr(course, field, data[field])
        else:
            if 'save_draft' in self.data:
                data['status'] = PLANNED
            else:
                data['status'] = AVAILABLE
            course = Course(**data)
        course.save()
        course.teachers.clear()
        course.teachers.add(*teachers)
        course.partners.clear()
        course.partners.add(*partners)


class AddLessonForm(forms.Form):
    date = forms.DateTimeField()
    course = forms.ModelChoiceField(queryset=Course.objects.all(), widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        course = kwargs.pop('course', None)
        super(AddLessonForm, self).__init__(*args, **kwargs)
        self.user = user
        if course:
            self.fields['course'].initial = course.pk

    def clean(self):
        form_data = self.cleaned_data
        course = form_data['course']
        user = self.user
        if user.is_moderator and user.city != course.theme.city:
            raise ValidationError("Moderator can not create a lesson in this course.")
        return form_data

    def save(self):
        data = self.cleaned_data
        lesson = Lesson(**data)
        lesson.save()
        return lesson


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
        self.partner = partner
        if user.is_moderator:
            self.fields['is_general'].widget = forms.HiddenInput()
            self.fields['is_general'].required = False
            self.fields['cities'].widget = forms.MultipleHiddenInput()
        if partner:
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
        partner = self.partner
        cities = data.pop('cities', [])
        if partner:
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
            else:
                self.initial.update({
                    'city': user.city,
                })
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
