from django.conf.urls import url, include, static
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    url(r'^admin/', include('academy_admin.urls')),
    url(r'^', include('academy_site.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
