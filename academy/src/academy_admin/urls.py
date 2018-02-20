from django.conf.urls import url

from . import views

app_name = 'academy_admin'
urlpatterns = [
    url(r'^$', views.homepage, name='homepage'),
    url(r'^cities/$', views.cities, name='cities'),
    url(r'^cities/add/$', views.add_city, name='add_city'),
    url(r'^cities/(?P<pk>\d+)/$', views.city_detail, name='city_detail'),
    url(r'^cities/(?P<pk>\d+)/delete/$', views.delete_city, name='delete_city'),
    url(r'^partners/$', views.partners, name='partners'),
    url(r'^partners/add/$', views.add_partner, name='add_partner'),
    url(r'^partners/(?P<pk>\d+)/$', views.partner_detail, name='partner_detail'),
    url(r'^partners/(?P<pk>\d+)/delete/$', views.delete_partner, name='delete_partner'),
    url(r'^themes/$', views.themes, name='themes'),
    url(r'^themes/add/$', views.add_theme, name='add_theme'),
    url(r'^themes/(?P<pk>\d+)/$', views.theme_detail, name='theme_detail'),
    url(r'^themes/(?P<pk>\d+)/delete/$', views.delete_theme, name='delete_theme'),
    url(r'^courses/$', views.courses, name='courses'),
    url(r'^courses/add/$', views.add_course, name='add_course'),
    url(r'^courses/(?P<pk>\d+)/$', views.course_detail, name='course_detail'),
    url(r'^courses/(?P<pk>\d+)/delete/$', views.delete_course, name='delete_course'),
    url(r'^teachers/$', views.teachers, name='teachers'),
    url(r'^teachers/add/$', views.add_teacher, name='add_teacher'),
    url(r'^teachers/(?P<pk>\d+)/delete/$', views.delete_teacher, name='delete_teacher'),
    url(r'^security/$', views.security, name='security'),
    url(r'^security/add/$', views.add_security, name='add_security'),
    url(r'^security/(?P<pk>\d+)/delete/$', views.delete_security, name='delete_security'),
    url(r'^users/(?P<pk>\d+)/$', views.user_detail, name='user_detail'),
    url(r'^users/profile/$', views.user_profile, name='user_profile'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^change-password/$', views.change_password, name='change_password'),
]
