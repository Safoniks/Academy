from django.conf.urls import url
from django.conf import settings
from django.contrib.auth.views import logout

from . import views

app_name = 'academy_site'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^signin/$', views.signin, name='signin'),
    url(r'^contact_us/$', views.contact_us, name='contact_us'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^profile/edit/$', views.profile_edit, name='profile_edit'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^(?P<city_slug>[\w-]+)/$', views.city_detail, name='city_detail'),
    url(r'^(?P<city_slug>[\w-]+)/(?P<theme_slug>[\w-]+)/$', views.theme_detail, name='theme_detail'),
]
