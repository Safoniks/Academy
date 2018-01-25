from django.conf.urls import url

from . import views

app_name = 'academy_admin'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add-city/$', views.add_city, name='add_city'),
    url(r'^cities/$', views.cities, name='cities'),
    url(r'^cities/(?P<slug>[\w-]+)/$', views.city_detail, name='city_detail'),
    url(r'^cities/(?P<slug>[\w-]+)/delete/$', views.delete_city, name='delete_city'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
]
