from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist

from .forms import LoginForm, AddCityForm, UpdateCityForm
from backend import login, logout
from decorators import admin_user_login_required, anonymous_user_required

from academy_site.models import City

AuthUser = get_user_model()


@anonymous_user_required(login_url='academy_admin:index')
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin/index.html')
                return redirect(redirect_to)
            else:
                form = LoginForm()
    else:
        form = LoginForm()
    return render(request, 'academy_admin/login.html', {
        'login_form': form,
    })


def logout_view(request):
    logout(request)
    return redirect('academy_admin:index')


@admin_user_login_required(login_url='academy_admin:login')
def index(request):
    context = {
        'user': request.user
    }
    return render(request, 'academy_admin/index.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def add_city(request):
    if request.method == 'POST':
        add_city_form = AddCityForm(request.POST, request.FILES)
        if add_city_form.is_valid():
            add_city_form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:cities')
            return redirect(redirect_to)
    else:
        add_city_form = AddCityForm()
    context = {
        'user': request.user,
        'add_city_form': add_city_form,
    }
    return render(request, 'academy_admin/add_city.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def cities(request):
    all_cities = City.objects.all()
    context = {
        'user': request.user,
        'cities': all_cities,
    }
    return render(request, 'academy_admin/cities.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def city_detail(request, slug):
    try:
        city = City.objects.get(slug=slug)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = UpdateCityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(city)
    else:
        city_data = {
            'description': city.description,
            'school_address': city.school_address,
            'email': city.email,
            'phone': city.phone,
            'photo': city.photo,
        }
        form = UpdateCityForm(initial=city_data)
    context = {
        'user': request.user,
        'city': city,
        'update_city_form': form,
    }
    return render(request, 'academy_admin/city_detail.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def delete_city(request, slug):
    try:
        city = City.objects.get(slug=slug)
    except ObjectDoesNotExist:
        raise Http404

    city.delete()
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:cities')
    return redirect(redirect_to)
