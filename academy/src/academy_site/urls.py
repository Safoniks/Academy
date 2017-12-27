from django.conf.urls import url

from . import views

app_name = 'academy_site'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
