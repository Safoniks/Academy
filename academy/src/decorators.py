from django.contrib.auth.decorators import user_passes_test
from django.conf import settings


def site_user_login_required(function=None, redirect_field_name=settings.REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_site_user,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def admin_user_login_required(function=None, redirect_field_name=settings.REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and (u.is_volunteer or u.is_admin),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator