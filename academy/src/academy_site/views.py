from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import send_mail

from .forms import SignUpForm, SignInForm, ContactUsForm, ProfileForm
from backend import login, logout
from decorators import site_user_login_required


from .models import SiteUser
AuthUser = get_user_model()


def home(request):
    context = {
        'user': request.user,
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
    else:
        signup_form = SignUpForm()
    context = {
        'user': request.user,
        'signup_form': signup_form,
        'signin_form': SignInForm(),
        'contact_us_form': ContactUsForm(),
    }
    return render(request, 'academy_site/home.html', context)


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
            else:
                signin_form = SignInForm()
    else:
        signin_form = SignInForm()
    context = {
        'user': request.user,
        'signup_form': SignUpForm(),
        'signin_form': signin_form,
        'contact_us_form': ContactUsForm(),
    }
    return render(request, 'academy_site/home.html', context)


def logout_view(request):
    logout(request)
    return redirect('academy_site:home')


def contact_us(request):
    if request.method == 'POST':
        contact_us_form = ContactUsForm(request.POST)
        if contact_us_form.is_valid():
            contact_us_form.contact_us()
    else:
        contact_us_form = ContactUsForm()
    context = {
        'user': request.user,
        'signup_form': SignUpForm(),
        'signin_form': SignInForm(),
        'contact_us_form': contact_us_form,
    }
    return render(request, 'academy_site/home.html', context)


@site_user_login_required(login_url='academy_site:signin')
def profile(request):
    context = {
        'user': request.user
    }
    return render(request, 'academy_site/profile.html', context)


@site_user_login_required(login_url='academy_site:signin')
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
