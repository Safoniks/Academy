from django.shortcuts import render


def index(request):
    context = {}
    return render(request, 'academy_admin/index.html', context)
