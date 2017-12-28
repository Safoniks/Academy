from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .forms import SignUpForm, SignInForm

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
            # form.save(commit=False)
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            if user and user.is_site_user:
                login(request, user)
            else:
                form = SignInForm()
    else:
        form = SignInForm()
    return render(request, 'academy_site/home.html', {
        'signin_form': form,
        'user': request.user
    })
