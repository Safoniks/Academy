from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import SignUpForm, SignInForm, ContactUsForm, ProfileForm
from backend import login, logout


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
            user = authenticate(request, email=email, password=password)
            print(user)
            login(request, user)
            redirect_to = request.GET.get('next', 'academy_site:home')
            return redirect(redirect_to)
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
            user = authenticate(request, email=email, password=password)
            if user and user.is_site_user:
                login(request, user)
                redirect_to = request.GET.get('next', 'academy_site:home')
                return redirect(redirect_to)
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


@login_required(login_url='academy_site:signin')
def profile(request):
    context = {
        'user': request.user
    }
    return render(request, 'academy_site/profile.html', context)


@login_required(login_url='academy_site:signin')
def profile_edit(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(user)
            redirect_to = request.GET.get('next', 'academy_site:profile')
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
