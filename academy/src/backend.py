from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.conf import settings
AuthUser = get_user_model()


class MyAuthenticationBackend:
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(AuthUser.USERNAME_FIELD)
        try:
            user = AuthUser._default_manager.get_by_natural_key(username)
        except AuthUser.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                if request.path.startswith(settings.ADMIN_URL):
                    if user.is_superuser or user.is_staff and user.is_active:
                        return user
                else:
                    if not user.is_superuser and not user.is_staff and user.is_active:
                        return user
                return None


def get_session_key(request):
    if request.path.startswith(settings.ADMIN_URL):
        session_key = settings.ADMIN_USER_SESSION_KEY
    else:
        session_key = settings.SITE_USER_SESSION_KEY
    return session_key


def get_user_session_key(request):
    return request.session.get(get_session_key(request), None)


def get_user(request):
    user_id = get_user_session_key(request)
    try:
        user = AuthUser.objects.get(pk=user_id)
    except AuthUser.DoesNotExist:
        return AnonymousUser()

    if request.path.startswith(settings.ADMIN_URL):
        if user.is_superuser or user.is_staff and user.is_active:
            return user
    else:
        if not user.is_superuser and not user.is_staff and user.is_active:
            return user
    return AnonymousUser()


def login(request, user):
    if user is None:
        user = request.user

    session_key = get_session_key(request)

    request.session[session_key] = str(user.pk)
    if hasattr(request, 'user'):
        request.user = user
    user_logged_in.send(sender=user.__class__, request=request, user=user)


def logout(request):
    user = getattr(request, 'user', None)
    if hasattr(user, 'is_authenticated') and not user.is_authenticated:
        user = None
    user_logged_out.send(sender=user.__class__, request=request, user=user)

    try:
        del request.session[get_session_key(request)]
    except KeyError:
        pass

    if hasattr(request, 'user'):
        request.user = AnonymousUser()
