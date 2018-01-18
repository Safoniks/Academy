from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render, redirect
from django.conf import settings

from .forms import LoginForm
from backend import login, logout
from decorators import admin_user_login_required, anonymous_user_required

AuthUser = get_user_model()


@admin_user_login_required(login_url='academy_admin:login')
def index(request):
    context = {
        'user': request.user
    }
    return render(request, 'academy_admin/index.html', context)


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
