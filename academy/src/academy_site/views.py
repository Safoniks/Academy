from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib import messages

from .forms import (
    SignUpForm,
    SignInForm,
    ContactUsForm,
    ProfileForm,
    SignUpCourseForm,
    ResetPasswordForm,
    ChangePassword,
)
from backend import login, logout
from decorators import site_user_login_required, anonymous_user_required
from utils import send_confirmation_email, generate_confirmation_code

from .models import City, Theme, Course, Teacher
AuthUser = get_user_model()


def home(request):
    cities = City.objects.all()

    context = {
        'user': request.user,
        'cities': cities,
        'signup_form': SignUpForm(),
        'signin_form': SignInForm(),
        'contact_us_form': ContactUsForm(),
        'reset_password_form': ResetPasswordForm(),
    }
    return render(request, 'academy_site/home.html', context)


@anonymous_user_required(login_url='academy_site:home')
def signup(request):
    if request.method == 'POST':
        signup_form = SignUpForm(request.POST)
        if signup_form.is_valid():
            signup_form.save()
            email = signup_form.cleaned_data.get('email')
            password = signup_form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            login(request, user)
            send_confirmation_email(user)
            messages.success(request, 'Підтвердження емейла на почті')
        else:
            messages.error(request, 'Error')
        redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:home')
        return redirect(redirect_to)
    else:
        raise Http404


@anonymous_user_required(login_url='academy_site:home')
def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            form.send_email()
            messages.success(request, 'Новий пароль на почті.')
        else:
            messages.error(request, 'Error')
        redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:home')
        return redirect(redirect_to)
    else:
        raise Http404


@site_user_login_required(login_url='academy_site:home')
def change_password(request):
    user = request.user
    if request.method == 'POST':
        form = ChangePassword(request.POST, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your password was successfully updated!')
        else:
            messages.error(request, 'Error')
        redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:profile')
        return redirect(redirect_to)
    else:
        raise Http404


def email_confirm(request, user_id, code):
    activation_expired = False
    already_active = False
    user = get_object_or_404(AuthUser, id=user_id, siteuser__confirmation_code=code)
    if not user.siteuser.is_confirmed:
        if timezone.now() > user.siteuser.confirmation_code_expires:
            activation_expired = True #Display: offer the user to send a new activation link
            messages.error(request, 'Лінка вже не дійсна')
        else:
            user.siteuser.is_confirmed = True
            user.siteuser.save()
            messages.success(request, 'Email підтверджено')

    else:
        already_active = True #Display : error message
        messages.error(request, 'Вже підтвержено')
    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:home')
    return redirect(redirect_to)


@site_user_login_required(login_url='academy_site:home')
def new_confirmation_code(request):
    user = request.user
    if not user.siteuser.is_confirmed:
        user.siteuser.confirmation_code = generate_confirmation_code(user.email)
        user.siteuser.confirmation_code_expires = timezone.now() + settings.SIGNUP_CONFIRMATION_CODE_EXPIRE
        user.siteuser.save()

        send_confirmation_email(user)
        messages.success(request, 'Підтвердження емейла на почті')
    else:
        raise Http404

    redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:home')
    return redirect(redirect_to)


@anonymous_user_required(login_url='academy_site:home')
def signin(request):
    if request.method == 'POST':
        signin_form = SignInForm(request.POST)
        if signin_form.is_valid():
            email = signin_form.cleaned_data.get('email')
            password = signin_form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
        else:
            messages.error(request, 'Error')
        redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:home')
        return redirect(redirect_to)
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
            messages.success(request, 'Відправлено')
        else:
            messages.error(request, 'Error')
        redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:home')
        return redirect(redirect_to)
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
        form = ProfileForm(request.POST, request.FILES, user=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль оновлено')
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:profile')
            return redirect(redirect_to)
    else:
        form = ProfileForm(user=user)
    context = {
        'user': user,
        'edit_form': form,
        'change_password_form': ChangePassword(),
    }
    return render(request, 'academy_site/profile_edit.html', context)


def city_detail(request, city_slug):
    try:
        city = City.objects.get(slug=city_slug)
    except ObjectDoesNotExist:
        raise Http404

    context = {
        'user': request.user,
        'signup_form': SignUpForm(),
        'signin_form': SignInForm(),
        'city': city,
        'teachers': Teacher.objects.filter(auth_user__city=city),
        'contact_us_form': ContactUsForm(),
        'reset_password_form': ResetPasswordForm(),
    }
    return render(request, 'academy_site/city_detail.html', context)


def theme_detail(request, city_slug, theme_slug):
    try:
        theme = Theme.objects.get(city__slug=city_slug, slug=theme_slug)
    except ObjectDoesNotExist:
        raise Http404

    context = {
        'user': request.user,
        'signup_form': SignUpForm(),
        'signin_form': SignInForm(),
        'theme': theme,
        'reset_password_form': ResetPasswordForm(),
    }
    return render(request, 'academy_site/theme_detail.html', context)


def course_detail(request, city_slug, theme_slug, course_slug):
    try:
        course = Course.objects.get(theme__city__slug=city_slug, theme__slug=theme_slug, slug=course_slug)
    except ObjectDoesNotExist:
        raise Http404

    context = {
        'user': request.user,
        'signup_form': SignUpForm(),
        'signin_form': SignInForm(),
        'course': course,
        'reset_password_form': ResetPasswordForm(),
    }
    return render(request, 'academy_site/course_detail.html', context)


def signup_course(request, city_slug, theme_slug, course_slug):
    user = request.user
    try:
        course = Course.objects.get(theme__city__slug=city_slug, theme__slug=theme_slug, slug=course_slug)
    except ObjectDoesNotExist:
        raise Http404
    if request.method == 'POST':
        form = SignUpCourseForm(request.POST, request.FILES, user=user, course=course)
        if form.is_valid():
            form.save()
            redirect_to = request.GET.get(settings.REDIRECT_FIELD_NAME, 'academy_site:course_detail')
            return redirect(redirect_to, city_slug=city_slug, theme_slug=theme_slug, course_slug=course_slug)
    else:
        form = SignUpCourseForm(user=user, course=course)
    context = {
        'user': user,
        'signup_form': SignUpForm(),
        'signin_form': SignInForm(),
        'course': course,
        'form': form,
        'reset_password_form': ResetPasswordForm(),
    }
    return render(request, 'academy_site/signup_course.html', context)
