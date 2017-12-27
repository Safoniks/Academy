from django.shortcuts import render
from django.contrib.auth import get_user_model


def index(request):
    context = {}
    return render(request, 'academy_site/index.html', context)
