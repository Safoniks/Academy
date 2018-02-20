from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.conf import settings


def anonymous_required(function=None, redirect_field_name=settings.REDIRECT_FIELD_NAME, redirect_url=None):
    def _dec(view_func):
        def _view(request, *args, **kwargs):
            u = request.user
            if u.is_authenticated:
                url = None if redirect_url is None else resolve_url(redirect_url)
                if redirect_field_name and redirect_field_name in request.GET:
                    url = request.GET[redirect_field_name]
                if not url:
                    url = resolve_url(u.get_default_page())
                return HttpResponseRedirect(url)
            else:
                return view_func(request, *args, **kwargs)

        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)


def superuser_required(function=None, redirect_field_name=settings.REDIRECT_FIELD_NAME, redirect_url=None):
    def _dec(view_func):
        def _view(request, *args, **kwargs):
            u = request.user
            if not u.is_superuser:
                url = None if redirect_url is None else resolve_url(redirect_url)
                if redirect_field_name and redirect_field_name in request.GET:
                    url = request.GET[redirect_field_name]
                if not url:
                    # url = resolve_url(u.get_default_page())
                    return HttpResponseForbidden()
                return HttpResponseRedirect(url)
            else:
                return view_func(request, *args, **kwargs)

        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)


def moderator_required(function=None, redirect_field_name=settings.REDIRECT_FIELD_NAME, redirect_url=None):
    def _dec(view_func):
        def _view(request, *args, **kwargs):
            u = request.user
            if not u.is_admin:
                url = None if redirect_url is None else resolve_url(redirect_url)
                if redirect_field_name and redirect_field_name in request.GET:
                    url = request.GET[redirect_field_name]
                if not url:
                    # url = resolve_url(u.get_default_page())
                    return HttpResponseForbidden()
                return HttpResponseRedirect(url)
            else:
                return view_func(request, *args, **kwargs)

        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    if function is None:
        return _dec
    else:
        return _dec(function)


def site_user_login_required(function=None, redirect_field_name=settings.REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_site_user,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def staff_user_login_required(function=None, redirect_field_name=settings.REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def permission_required(*perms, function=None, redirect_field_name=settings.REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: any(u.has_perm(perm) for perm in perms),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
