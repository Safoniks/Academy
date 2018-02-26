from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render, redirect, resolve_url
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist

from .forms import (
    LoginForm,
    CityForm,
    PartnerForm,
    ThemeForm,
    CourseForm,
    CreateBackOfficeUserForm,
    EditBackOfficeUserForm,
    ProfileForm,
    ChangePasswordForm,
    AddLessonForm,
)
from backend import login, logout
from decorators import (
    anonymous_required,
    staff_user_login_required,
    moderator_required,
    superuser_required,
)

from academy_site.models import City, Partner, AdminProfile, Theme, Course, Lesson
from academy_site.choices import *

AuthUser = get_user_model()


@anonymous_required
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, user.get_default_page())
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
    return redirect('academy_admin:login')


@staff_user_login_required(login_url='academy_admin:login')
def change_password(request):
    user = request.user
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, user.get_default_page())
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST, user=user)
        if form.is_valid():
            form.save()
        return redirect(redirect_to)
    else:
        raise Http404


@staff_user_login_required(login_url='academy_admin:login')
@superuser_required
def homepage(request):
    context = {
        'user': request.user
    }
    return render(request, 'academy_admin/homepage.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@superuser_required
def add_city(request):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:cities')
    if request.method == 'POST':
        add_city_form = CityForm(request.POST, request.FILES)
        if add_city_form.is_valid():
            add_city_form.save()
            return redirect(redirect_to)
    else:
        add_city_form = CityForm()
    context = {
        'user': request.user,
        'add_city_form': add_city_form,
    }
    return render(request, 'academy_admin/add_city.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def cities(request):
    user = request.user
    cities_qs = City.objects.all()
    if not user.is_administrator:
        cities_qs = cities_qs.filter(authuser=user)
    context = {
        'user': user,
        'cities': cities_qs,
    }
    return render(request, 'academy_admin/cities.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def city_detail(request, pk):
    user = request.user
    city_qs = City.objects.filter(pk=pk)
    if not user.is_administrator:
        city_qs = city_qs.filter(authuser=user)
    city = city_qs.first()
    if not city:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CityForm(request.POST, request.FILES, city=city)
        if form.is_valid():
            form.save()
    else:
        form = CityForm(city=city)
    context = {
        'user': user,
        'city': city,
        'teachers': AuthUser.objects.teachers(city=city),
        'update_city_form': form,
    }
    return render(request, 'academy_admin/city_detail.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@superuser_required
def delete_city(request, pk):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:cities')
    try:
        city = City.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    city.delete()
    return redirect(redirect_to)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def themes(request):
    user = request.user
    selected_city_pk = request.GET.get('city', None)

    if not selected_city_pk or user.is_moderator:
        selected_city_pk = getattr(user.city, 'pk', None)

    all_cities = City.objects.all()
    try:
        if selected_city_pk:
            selected_city = all_cities.get(pk=selected_city_pk)
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        selected_city = all_cities.first()

    city_themes = Theme.objects.filter(city=selected_city)
    context = {
        'user': user,
        'themes': city_themes,
        'cities': all_cities,
        'selected_city': selected_city,
    }
    return render(request, 'academy_admin/themes.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def add_theme(request):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:themes')
    user = request.user

    selected_city_pk = request.GET.get('city', None)
    try:
        selected_city = City.objects.get(pk=selected_city_pk)
    except ObjectDoesNotExist:
        selected_city = None

    if request.method == 'POST':
        form = ThemeForm(request.POST, request.FILES, user=user, city=selected_city)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        form = ThemeForm(user=user, city=selected_city)
    context = {
        'user': user,
        'add_theme_form': form,
    }
    return render(request, 'academy_admin/add_theme.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def theme_detail(request, pk):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:themes')
    user = request.user
    try:
        theme = Theme.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    if user.is_moderator and user.city != theme.city:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = ThemeForm(request.POST, request.FILES, user=user, theme=theme)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        form = ThemeForm(user=user, theme=theme)
    context = {
        'user': user,
        'theme': theme,
        'update_theme_form': form,
    }
    return render(request, 'academy_admin/theme_detail.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def delete_theme(request, pk):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:themes')
    user = request.user
    try:
        theme = Theme.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    if user.is_moderator and user.city != theme.city:
        return HttpResponseForbidden()

    theme.delete()
    return redirect(redirect_to)


@staff_user_login_required(login_url='academy_admin:login')
def courses(request):
    user = request.user
    selected_city_pk = request.GET.get('city', None)
    selected_theme_pk = request.GET.get('theme', None)
    selected_status = request.GET.get('status', None)

    if not selected_city_pk or not user.is_administrator:
        selected_city_pk = getattr(user.city, 'pk', None)

    all_cities = City.objects.all()
    try:
        if selected_city_pk:
            selected_city = all_cities.get(pk=selected_city_pk)
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        selected_city = all_cities.first()

    city_themes = Theme.objects.filter(city=selected_city)
    try:
        if selected_theme_pk:
            selected_theme = city_themes.get(pk=selected_theme_pk)
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        selected_theme = city_themes.first()

    theme_courses = Course.objects.filter(theme=selected_theme)
    if selected_status:
        theme_courses = theme_courses.filter(status=selected_status)
    my_courses = Course.objects.all()
    context = {
        'user': user,
        'courses': theme_courses,
        'my_courses': my_courses,
        'status_choices': (status[0] for status in STATUS_CHOICES),
        'cities': all_cities,
        'themes': city_themes,
        'selected_status': selected_status,
        'selected_city': selected_city,
        'selected_theme': selected_theme,
    }
    return render(request, 'academy_admin/courses.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def add_course(request):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:courses')
    user = request.user
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        selected_city_pk = request.GET.get('city', None)

        if not selected_city_pk or user.is_moderator:
            selected_city_pk = getattr(user.city, 'pk', None)

        all_cities = City.objects.all()
        try:
            if selected_city_pk:
                selected_city = all_cities.get(pk=selected_city_pk)
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

        selected_theme_pk = request.GET.get('theme', None)
        try:
            selected_theme = city_themes.get(pk=selected_theme_pk)
        except ObjectDoesNotExist:
            selected_theme = None

        form = CourseForm(selected_theme=selected_theme, **form_selects)
        context = {
            'user': user,
            'cities': all_cities,
            'selected_city': selected_city,
            'add_course_form': form,
        }
        return render(request, 'academy_admin/add_course.html', context)


@staff_user_login_required(login_url='academy_admin:login')
def course_detail(request, pk):
    user = request.user
    try:
        course = Course.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404
    course_city = course.theme.city

    if not user.is_administrator and user not in course.teachers.all() and user.city != course_city:
        return HttpResponseForbidden()

    city_themes = course_city.theme_set.all()
    city_teachers = AuthUser.objects.teachers(city=course_city)
    city_partners = course_city.partners.all()
    form_selects = {
        'themes': city_themes,
        'teachers': city_teachers,
        'partners': city_partners,
    }

    if request.method == 'POST':
        if user.is_teacher:
            return HttpResponseForbidden()
        update_course_form = CourseForm(request.POST, request.FILES, course=course, **form_selects)
        if update_course_form.is_valid():
            update_course_form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, course.get_admin_url())
            return redirect(redirect_to)
    else:
        update_course_form = CourseForm(course=course, **form_selects)
    context = {
        'user': user,
        'course': course,
        'add_lesson_form': AddLessonForm(course=course),
        'update_course_form': update_course_form,
    }
    return render(request, 'academy_admin/course_detail.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def delete_course(request, pk):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:courses')
    user = request.user
    try:
        course = Course.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    if user.is_moderator and user.city != course.theme.city:
        return HttpResponseForbidden()

    course.delete()
    return redirect(redirect_to)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def add_lesson(request):
    user = request.user

    if request.method == 'POST':
        form = AddLessonForm(request.POST, user=user)
        if form.is_valid():
            lesson = form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, lesson.course.get_admin_url())
            return redirect(redirect_to)
        return HttpResponse(400)
    else:
        raise Http404


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def delete_lesson(request, pk):
    user = request.user
    try:
        lesson = Lesson.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    if user.is_moderator and user.city != lesson.course.theme.city:
        return HttpResponseForbidden()
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, lesson.course.get_admin_url())

    lesson.delete()
    return redirect(redirect_to)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def partners(request):
    user = request.user
    context = {}
    selected_city_pk = request.GET.get('city', None)
    is_main = request.GET.get('main', None) is not None
    if is_main and user.is_administrator:
        all_partners = Partner.objects.filter(is_general=True)
    else:
        if not selected_city_pk or user.is_moderator:
            selected_city_pk = getattr(user.city, 'pk', None)

        all_cities = City.objects.all()
        try:
            if selected_city_pk:
                selected_city = all_cities.get(pk=selected_city_pk)
            else:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            selected_city = all_cities.first()

        all_partners = Partner.objects.filter(city=selected_city)
        context.update({
            'cities': all_cities,
            'selected_city': selected_city,
        })
    context.update({
        'user': request.user,
        'partners': all_partners,
        'is_main': is_main,
    })
    return render(request, 'academy_admin/partners.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def add_partner(request):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:partners')
    user = request.user

    selected_city_pk = request.GET.get('city', None)
    try:
        selected_city = City.objects.get(pk=selected_city_pk)
    except ObjectDoesNotExist:
        selected_city = None

    if request.method == 'POST':
        form = PartnerForm(request.POST, request.FILES, user=user, city=selected_city)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        form = PartnerForm(user=user, city=selected_city)
    context = {
        'user': user,
        'add_partner_form': form,
    }
    return render(request, 'academy_admin/add_partner.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def partner_detail(request, pk):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:partners')
    user = request.user
    try:
        partner = Partner.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    if user.is_moderator and user.city not in partner.city_set.all():
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = PartnerForm(request.POST, request.FILES, user=user, partner=partner)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        form = PartnerForm(user=user, partner=partner)
    context = {
        'user': request.user,
        'partner': partner,
        'update_partner_form': form,
    }
    return render(request, 'academy_admin/partner_detail.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def delete_partner(request, pk):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:partners')
    user = request.user

    selected_city_pk = request.GET.get('city', None)
    try:
        selected_city = City.objects.get(pk=selected_city_pk)
    except ObjectDoesNotExist:
        selected_city = None

    try:
        partner = Partner.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404

    partner_cities = partner.city_set.all()
    if user.is_moderator:
        if user.city not in partner_cities:
            return HttpResponseForbidden()
        else:
            selected_city = user.city

    if selected_city:
        if len(partner_cities) > 1 or partner.is_general:
            partner.city_set.remove(selected_city)
            return redirect(redirect_to)

    partner.delete()
    return redirect(redirect_to)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def teachers(request):
    user = request.user
    selected_city_pk = request.GET.get('city', None)
    if not selected_city_pk or user.is_moderator:
        selected_city_pk = getattr(user.city, 'pk', None)

    all_cities = City.objects.all()
    try:
        if selected_city_pk:
            selected_city = all_cities.get(pk=selected_city_pk)
        else:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        selected_city = all_cities.first()

    all_teachers = AuthUser.objects.teachers(city=selected_city)
    context = {
        'user': user,
        'teachers': all_teachers,
        'cities': all_cities,
        'selected_city': selected_city,
    }
    return render(request, 'academy_admin/teachers.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def add_teacher(request):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:teachers')
    user = request.user

    selected_city_pk = request.GET.get('city', None)
    try:
        selected_city = City.objects.get(pk=selected_city_pk)
    except ObjectDoesNotExist:
        selected_city = None

    if request.method == 'POST':
        form = CreateBackOfficeUserForm(request.POST, request.FILES, request=request, city=selected_city)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        form = CreateBackOfficeUserForm(request=request, city=selected_city)
    context = {
        'user': user,
        'add_teacher_form': form,
    }
    return render(request, 'academy_admin/add_teacher.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def delete_teacher(request, pk):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:teachers')
    user = request.user
    try:
        teacher = AuthUser.objects.get(pk=pk)
        if not teacher.is_teacher:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        raise Http404

    if (teacher == request.user) or (
                user.is_moderator and user.city != teacher.city):
        return HttpResponseForbidden()

    teacher.delete()
    return redirect(redirect_to)


@staff_user_login_required(login_url='academy_admin:login')
@superuser_required
def security(request):
    admins = AuthUser.objects.admins()
    context = {
        'user': request.user,
        'admins': admins,
    }
    return render(request, 'academy_admin/security.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@superuser_required
def add_security(request):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:security')
    if request.method == 'POST':
        form = CreateBackOfficeUserForm(request.POST, request.FILES, request=request)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        form = CreateBackOfficeUserForm(request=request)
    context = {
        'user': request.user,
        'add_security_form': form,
    }
    return render(request, 'academy_admin/add_security.html', context)


@staff_user_login_required(login_url='academy_admin:login')
@superuser_required
def delete_security(request, pk):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:security')
    try:
        user = AuthUser.objects.get(pk=pk)
        if not (user.is_superuser or user.is_admin):
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        raise Http404

    if user == request.user:
        return HttpResponseForbidden()

    user.delete()
    return redirect(redirect_to)


@staff_user_login_required(login_url='academy_admin:login')
@moderator_required
def user_detail(request, pk):
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_admin:teachers')
    user = request.user
    try:
        back_office_user = AuthUser.objects.get(pk=pk)
        if not back_office_user.is_staff:
            raise ObjectDoesNotExist
    except ObjectDoesNotExist:
        raise Http404

    if user.is_moderator and user.city != back_office_user.city:
        return HttpResponseForbidden()

    if request.method == 'POST' and user.is_administrator:
        form = EditBackOfficeUserForm(request.POST, request.FILES, back_office_user=back_office_user)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        if user.is_moderator:
            form = None
        else:
            form = EditBackOfficeUserForm(back_office_user=back_office_user)
    context = {
        'user': user,
        'back_office_user': back_office_user,
        'form': form,
    }
    return render(request, 'academy_admin/user_detail.html', context)


@staff_user_login_required(login_url='academy_admin:login')
def user_profile(request):
    user = request.user
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, user.get_default_page())
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        form = ProfileForm(user=user)
    context = {
        'user': user,
        'profile_form': form,
        'change_password_form': ChangePasswordForm(),
    }
    return render(request, 'academy_admin/user_profile.html', context)
