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
    url(r'^logout/$', logout, {'next_page': settings.SITE_LOGOUT_REDIRECT_URL}, name='logout'),
]
