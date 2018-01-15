from .backend import get_user
from django.utils.deprecation import MiddlewareMixin


class MyAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = get_user(request)
