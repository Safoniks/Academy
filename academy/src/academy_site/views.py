from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist

from .forms import SignUpForm, SignInForm, ContactUsForm, ProfileForm
from backend import login, logout
from decorators import site_user_login_required


from .models import City, Theme
AuthUser = get_user_model()


def home(request):
    cities = City.objects.all()

    context = {
        'user': request.user,
        'cities': cities,
        'signup_form': SignUpForm(),
        'signin_form': SignInForm(),
        'contact_us_form': ContactUsForm(),
    }
    return render(request, 'academy_site/home.html', context)


def signup(request):
    if request.method == 'POST':
        signup_form = SignUpForm(request.POST)
        if signup_form.is_valid():
            signup_form.save()
            email = signup_form.cleaned_data.get('email')
            password = signup_form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            login(request, user)
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:home')
            return redirect(redirect_to)
        return HttpResponse('400')
    else:
        raise Http404


def signin(request):
    if request.method == 'POST':
        signin_form = SignInForm(request.POST)
        if signin_form.is_valid():
            email = signin_form.cleaned_data.get('email')
            password = signin_form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:home')
                return redirect(redirect_to)
        return HttpResponse('400')
    else:
        raise Http404


def logout_view(request):
    logout(request)
    return redirect('academy_site:home')


def contact_us(request):
    if request.method == 'POST':
        contact_us_form = ContactUsForm(request.POST)
        if contact_us_form.is_valid():
            contact_us_form.contact_us()
            return HttpResponse('200')
        else:
            return HttpResponse('400')
    else:
        raise Http404


@site_user_login_required(login_url='academy_site:home')
def profile(request):
    context = {
        'user': request.user
    }
    return render(request, 'academy_site/profile.html', context)


@site_user_login_required(login_url='academy_site:home')
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(user)
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:profile')
            return redirect(redirect_to)
    else:
        user_profile_data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'photo': user.photo,
            'birthdate': user.siteuser.birthdate,
            'phone': user.siteuser.phone,
            'address': user.siteuser.address,
            'postcode': user.siteuser.postcode,
        }
        form = ProfileForm(initial=user_profile_data)
    context = {
        'user': user,
        'edit_form': form,
    }
    return render(request, 'academy_site/profile_edit.html', context)


@site_user_login_required(login_url='academy_site:home')
def city_detail(request, city_slug):
    try:
        city = City.objects.get(slug=city_slug)
    except ObjectDoesNotExist:
        raise Http404

    context = {
        'user': request.user,
        'city': city,
        'teachers': AuthUser.objects.teachers(city=city),
        'contact_us_form': ContactUsForm(),
    }
    return render(request, 'academy_site/city_detail.html', context)


@site_user_login_required(login_url='academy_site:home')
def theme_detail(request, city_slug, theme_slug):
    try:
        theme = Theme.objects.get(city__slug=city_slug, slug=theme_slug)
    except ObjectDoesNotExist:
        raise Http404

    context = {
        'user': request.user,
        'theme': theme,
    }
    return render(request, 'academy_site/theme_detail.html', context)
