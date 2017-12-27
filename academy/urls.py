from django.conf.urls import url, include
from django.conf import settings

urlpatterns = [
    url(r'^admin/', include('academy_admin.urls')),
    url(r'^', include('academy_site.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
