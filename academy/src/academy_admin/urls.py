from django.conf.urls import url

from . import views

app_name = 'academy_admin'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
