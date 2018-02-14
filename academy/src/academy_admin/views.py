from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist

from .forms import (
    LoginForm,
    CityForm,
    PartnerForm,
    TeacherForm,
    ThemeForm,
    AddCourseForm,
    SecurityForm,
)
from backend import login, logout
from decorators import admin_user_login_required, anonymous_user_required

from academy_site.models import City, Partner, AdminProfile, Theme, Course

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
        add_city_form = CityForm(request.POST, request.FILES)
        if add_city_form.is_valid():
            add_city_form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:cities')
            return redirect(redirect_to)
    else:
        add_city_form = CityForm()
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
def city_detail(request, pk):
    try:
        city = City.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = CityForm(request.POST, request.FILES, city=city)
        if form.is_valid():
            form.save()
    else:
        form = CityForm(city=city)
    context = {
        'user': request.user,
        'city': city,
        'teachers': AuthUser.objects.teachers(city=city),
        'update_city_form': form,
    }
    return render(request, 'academy_admin/city_detail.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def delete_city(request, pk):
    try:
        city = City.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    city.delete()
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:cities')
    return redirect(redirect_to)


@admin_user_login_required(login_url='academy_admin:login')
def partners(request):
    all_partners = Partner.objects.all()
    context = {
        'user': request.user,
        'partners': all_partners,
    }
    return render(request, 'academy_admin/partners.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def add_partner(request):
    if request.method == 'POST':
        form = PartnerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:partners')
            return redirect(redirect_to)
    else:
        form = PartnerForm()
    context = {
        'user': request.user,
        'add_partner_form': form,
    }
    return render(request, 'academy_admin/add_partner.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def partner_detail(request, pk):
    try:
        partner = Partner.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = PartnerForm(request.POST, request.FILES, partner=partner)
        if form.is_valid():
            form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:partners')
            return redirect(redirect_to)
    else:
        form = PartnerForm(partner=partner)
    context = {
        'user': request.user,
        'partner': partner,
        'update_partner_form': form,
    }
    return render(request, 'academy_admin/partner_detail.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def delete_partner(request, pk):
    try:
        partner = Partner.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    partner.delete()
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:partners')
    return redirect(redirect_to)


@admin_user_login_required(login_url='academy_admin:login')
def teachers(request):
    all_teachers = AuthUser.objects.teachers()
    context = {
        'user': request.user,
        'teachers': all_teachers,
    }
    return render(request, 'academy_admin/teachers.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:teachers')
            return redirect(redirect_to)
    else:
        form = TeacherForm()
    context = {
        'user': request.user,
        'add_teacher_form': form,
    }
    return render(request, 'academy_admin/add_teacher.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def teacher_detail(request, pk):
    try:
        teacher = AuthUser.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, teacher=teacher)
        if form.is_valid():
            form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:teachers')
            return redirect(redirect_to)
    else:
        form = TeacherForm(teacher=teacher)
    context = {
        'user': request.user,
        'teacher': teacher,
        'update_teacher_form': form,
    }
    return render(request, 'academy_admin/teacher_detail.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def delete_teacher(request, pk):
    try:
        teacher = AuthUser.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    teacher.auth_user.delete()
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:teachers')
    return redirect(redirect_to)


@admin_user_login_required(login_url='academy_admin:login')
def themes(request):
    selected_city_slug = request.GET.get('city', None)

    all_cities = City.objects.all()
    try:
        if selected_city_slug:
            selected_city = all_cities.get(slug=selected_city_slug)
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        selected_city = all_cities.first()

    city_themes = Theme.objects.filter(city=selected_city)
    context = {
        'user': request.user,
        'themes': city_themes,
        'cities': all_cities,
        'selected_city': selected_city,
    }
    return render(request, 'academy_admin/themes.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def add_theme(request):
    if request.method == 'POST':
        form = ThemeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:themes')
            return redirect(redirect_to)
    else:
        form = ThemeForm()
    context = {
        'user': request.user,
        'add_theme_form': form,
    }
    return render(request, 'academy_admin/add_theme.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def theme_detail(request, pk):
    try:
        theme = Theme.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = ThemeForm(request.POST, request.FILES, theme=theme)
        if form.is_valid():
            form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:themes')
            return redirect(redirect_to)
    else:
        form = ThemeForm(theme=theme)
    context = {
        'user': request.user,
        'theme': theme,
        'update_theme_form': form,
    }
    return render(request, 'academy_admin/theme_detail.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def delete_theme(request, pk):
    try:
        theme = Theme.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    theme.delete()
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:themes')
    return redirect(redirect_to)


@admin_user_login_required(login_url='academy_admin:login')
def courses(request):
    selected_city_slug = request.GET.get('city', None)
    selected_theme_slug = request.GET.get('theme', None)

    all_cities = City.objects.all()
    try:
        if selected_city_slug:
            selected_city = all_cities.get(slug=selected_city_slug)
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        selected_city = all_cities.first()

    city_themes = Theme.objects.filter(city=selected_city)
    try:
        if selected_theme_slug:
            selected_theme = city_themes.get(slug=selected_theme_slug)
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        selected_theme = city_themes.first()

    theme_courses = Course.objects.filter(theme=selected_theme)
    context = {
        'user': request.user,
        'courses': theme_courses,
        'cities': all_cities,
        'themes': city_themes,
        'selected_city': selected_city,
        'selected_theme': selected_theme,
    }
    return render(request, 'academy_admin/courses.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def add_course(request):
    if request.method == 'POST':
        form = AddCourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:courses')
            return redirect(redirect_to)
    else:
        selected_city_slug = request.GET.get('city', None)

        all_cities = City.objects.all()
        try:
            if selected_city_slug:
                selected_city = all_cities.get(slug=selected_city_slug)
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            selected_city = all_cities.first()

        city_themes = selected_city.theme_set.all()
        city_teachers = AuthUser.objects.teachers(city=selected_city)
        city_partners = selected_city.partners.all()
        form_selects = {
            'themes': city_themes,
            'teachers': city_teachers,
            'partners': city_partners,
        }

        form = AddCourseForm(**form_selects)
        context = {
            'user': request.user,
            'cities': all_cities,
            'selected_city': selected_city,
            'add_course_form': form,
        }
        return render(request, 'academy_admin/add_course.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def delete_course(request, pk):
    try:
        course = Course.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    course.delete()
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:courses')
    return redirect(redirect_to)


@admin_user_login_required(login_url='academy_admin:login')
def security(request):
    admins = AuthUser.objects.admins()
    context = {
        'user': request.user,
        'admins': admins,
    }
    return render(request, 'academy_admin/security.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def add_security(request):
    if request.method == 'POST':
        form = SecurityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:security')
            return redirect(redirect_to)
    else:
        form = SecurityForm()
    context = {
        'user': request.user,
        'add_security_form': form,
    }
    return render(request, 'academy_admin/add_security.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def security_detail(request, pk):
    try:
        admin = AuthUser.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    if request.method == 'POST':
        form = SecurityForm(request.POST, request.FILES, admin=admin)
        if form.is_valid():
            form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:security')
            return redirect(redirect_to)
    else:
        form = SecurityForm(admin=admin)
    context = {
        'user': request.user,
        'admin': admin,
        'form': form,
    }
    return render(request, 'academy_admin/security_detail.html', context)


@admin_user_login_required(login_url='academy_admin:login')
def delete_security(request, pk):
    try:
        admin = AuthUser.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    admin.delete()
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:security')
    return redirect(redirect_to)
