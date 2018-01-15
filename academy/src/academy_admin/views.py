from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from backend import login, logout

AuthUser = get_user_model()


def index(request):
    context = {}
    return render(request, 'academy_admin/index.html', context)
