from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import SignUpForm, SignInForm, ContactUsForm, ProfileForm


from .models import SiteUser
AuthUser = get_user_model()


def home(request):
    context = {
        'user': request.user
    }
    return render(request, 'academy_site/home.html', context)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            login(request, user)
            return redirect('academy_site:home')
    else:
        form = SignUpForm()
    return render(request, 'academy_site/home.html', {
        'signup_form': form,
        'user': request.user
    })


def signin(request):
    if request.method == 'POST':
        form = SignInForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user and user.is_site_user:
                login(request, user)
                return redirect('academy_site:home')
            else:
                form = SignInForm()
    else:
        form = SignInForm()
    return render(request, 'academy_site/home.html', {
        'signin_form': form,
        'user': request.user
    })


def contact_us(request):
    if request.method == 'POST':
        form = ContactUsForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ContactUsForm()
    return render(request, 'academy_site/home.html', {
        'contact_us_form': form,
        'user': request.user
    })


@login_required
def profile(request):
    context = {
        'user': request.user
    }
    return render(request, 'academy_site/profile.html', context)


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ProfileForm()
    context = {
        'user': request.user,
        'edit_form': form,
    }
    return render(request, 'academy_site/profile_edit.html', context)
