from django.conf.urls import url

from . import views

app_name = 'academy_admin'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^cities/$', views.cities, name='cities'),
    url(r'^cities/add/$', views.add_city, name='add_city'),
    url(r'^cities/(?P<slug>[\w-]+)/$', views.city_detail, name='city_detail'),
    url(r'^cities/(?P<slug>[\w-]+)/delete/$', views.delete_city, name='delete_city'),
    url(r'^partners/$', views.partners, name='partners'),
    url(r'^partners/add/$', views.add_partner, name='add_partner'),
    url(r'^partners/(?P<pk>\d+)/$', views.partner_detail, name='partner_detail'),
    url(r'^partners/(?P<pk>\d+)/delete/$', views.delete_partner, name='delete_partner'),
    url(r'^teachers/add/$', views.add_teacher, name='add_teacher'),
    url(r'^teachers/(?P<pk>\d+)/$', views.teacher_detail, name='teacher_detail'),
    url(r'^teachers/(?P<pk>\d+)/delete/$', views.delete_teacher, name='delete_teacher'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
]
