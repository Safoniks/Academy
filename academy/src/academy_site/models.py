import os
import uuid
from werkzeug.utils import secure_filename

from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


def get_image_path(instance, filename):
    photo_name = str(uuid.uuid4()) + '.' + secure_filename(filename).rsplit('.', 1)[-1]
    return os.path.join(settings.USER_PHOTOS_DIR_NAME, photo_name)


class AuthUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_admin(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Admin must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Admin must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)

    def create_volunteer(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Volunteer must have is_staff=True.')
        if extra_fields.get('is_superuser') is True:
            raise ValueError('Volunteer must have is_superuser=False.')
        return self._create_user(email, password, **extra_fields)

    def create_site_user(self, email, password, **extra_fields):
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is True:
            raise ValueError('Site user must have is_staff=False.')
        if extra_fields.get('is_superuser') is True:
            raise ValueError('Site user must have is_superuser=False.')
        return self._create_user(email, password, **extra_fields)


class AuthUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to=get_image_path, null=True, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    objects = AuthUserManager()

    class Meta:
        # app_label = 'academy_site'
        db_table = 'auth_user'
        verbose_name = 'authenticated user'
        verbose_name_plural = 'authenticated users'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return '{first_name} {last_name}'.format(first_name=self.first_name, last_name=self.last_name)

    @property
    def is_site_user(self):
        return hasattr(self, 'site_user') or self.is_staff is False and self.is_superuser is False

    @property
    def is_volunteer(self):
        return self.is_staff is True and self.is_superuser is False

    @property
    def is_admin(self):
        return self.is_superuser is True
