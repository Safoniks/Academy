from django.db import models
from django.conf import settings

from utils import get_image_path
from .choices import *


def get_course_photo_path(*args):
    return get_image_path(*args, dir_name=settings.CONTENT_PHOTOS_DIR_NAME)


class Content(models.Model):
    personal_name = models.CharField(max_length=50, choices=CONTENT_NAMES)
    data = models.CharField(max_length=500, null=True, blank=True)
    # photo = models.ImageField(upload_to=get_course_photo_path, null=True, blank=True)
    # language

    class Meta:
        db_table = 'content'
        verbose_name = 'content'
        verbose_name_plural = 'content'

    def __str__(self):
        return self.personal_name

    # def save(self, *args, **kwargs):
    #     try:
    #         this = self.__class__.objects.get(pk=self.pk)
    #         if this.photo != self.photo:
    #             this.photo.delete(save=False)
    #     except:
    #         pass
    #     super(self.__class__, self).save(*args, **kwargs)
    #
    # def delete(self, *args, **kwargs):
    #     ret = super(self.__class__, self).delete(*args, **kwargs)
    #     self.photo.delete(save=False)
    #     return ret
    #
    # def get_data(self):
    #     pass
