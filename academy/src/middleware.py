from .backend import get_user
from django.utils.deprecation import MiddlewareMixin
from academy_admin.choices import *
from academy_admin.models import Content
from django.core.exceptions import ObjectDoesNotExist


class MyAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = get_user(request)


class CommonContentMiddleware(MiddlewareMixin):
    def process_request(self, request):
        common_content = {}
        for content_name in CONTENT_MAP[COMMON]:
            try:
                content_data = Content.objects.get(personal_name=content_name).data
            except ObjectDoesNotExist:
                content_data = ''
            common_content[content_name] = content_data
        request.common_content = common_content
