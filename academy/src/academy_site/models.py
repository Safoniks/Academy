import os
import uuid
from werkzeug.utils import secure_filename

from django.conf import settings
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

from .validators import positive_number


def get_image_path(instance, filename, dir_name):
    photo_name = str(uuid.uuid4()) + '.' + secure_filename(filename).rsplit('.', 1)[-1]
    return os.path.join(dir_name, photo_name)


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


def get_user_photo_path(*args):
    return get_image_path(*args, dir_name=settings.USER_PHOTOS_DIR_NAME)


class AuthUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to=get_user_photo_path, null=True, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    objects = AuthUserManager()

    class Meta:
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


class SiteUser(models.Model):
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)
    phone = models.CharField(null=True, blank=True, max_length=20)
    address = models.CharField(null=True, blank=True, max_length=50)
    postcode = models.IntegerField(null=True, blank=True)
    # country
    # city
    # lessons

    class Meta:
        db_table = 'site_user'
        verbose_name = 'site user'
        verbose_name_plural = 'site users'


class ContactUs(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField()
    message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'contact_us'
        verbose_name = 'contact us'
        verbose_name_plural = 'contacts us'


def get_partner_logo_path(*args):
    return get_image_path(*args, dir_name=settings.PARTNER_LOGOS_DIR_NAME)


class Partner(models.Model):
    name = models.CharField(max_length=20)
    link = models.URLField()
    logo = models.ImageField(upload_to=get_partner_logo_path)

    class Meta:
        db_table = 'partner'
        verbose_name = 'partner'
        verbose_name_plural = 'partners'

    def __str__(self):
        return self.name


def get_city_photo_path(*args):
    return get_image_path(*args, dir_name=settings.CITY_PHOTOS_DIR_NAME)


class City(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    photo = models.ImageField(upload_to=get_city_photo_path, null=True, blank=True)
    school_address = models.CharField(max_length=100)
    last_update = models.DateTimeField(blank=True, null=True)
    partner = models.ManyToManyField(Partner)

    class Meta:
        db_table = 'city'
        verbose_name = 'city'
        verbose_name_plural = 'cities'

    def __str__(self):
        return self.name


def get_theme_photo_path(*args):
    return get_image_path(*args, dir_name=settings.THEME_PHOTOS_DIR_NAME)


class Theme(models.Model):
    name = models.CharField(max_length=50)
    photo = models.ImageField(upload_to=get_theme_photo_path, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)

    class Meta:
        db_table = 'theme'
        verbose_name = 'theme'
        verbose_name_plural = 'themes'

    def __str__(self):
        return self.name


class Lesson(models.Model):
    PLANNED = 'planned'
    AVAILABLE = 'available'
    CANCELLED = 'cancelled'
    SOLD_OUT = 'sold-out'
    ARCHIVED = 'archived'

    STATUS_CHOICES = (
        (PLANNED, PLANNED),
        (AVAILABLE, AVAILABLE),
        (CANCELLED, CANCELLED),
        (SOLD_OUT, SOLD_OUT),
        (ARCHIVED, ARCHIVED),
    )

    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    practise_info = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=100)
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    price_description = models.CharField(max_length=100, null=True, blank=True)
    seats = models.IntegerField(validators=[positive_number])
    remaining_seats = models.IntegerField(validators=[positive_number], blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    theme = models.ForeignKey(Theme, on_delete=models.CASCADE)
    partner = models.ManyToManyField(Partner)
    # teachers

    class Meta:
        db_table = 'lesson'
        verbose_name = 'lesson'
        verbose_name_plural = 'lessons'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.remaining_seats = self.seats
        super(Lesson, self).save(*args, **kwargs)


class LessonDate(models.Model):
    date = models.DateTimeField()
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    class Meta:
        db_table = 'lesson_date'
        verbose_name = 'lesson date'
        verbose_name_plural = 'lesson dates'


class UserLesson(models.Model):
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    know_academy_through = models.CharField(max_length=100, null=True, blank=True)
    questions = models.CharField(max_length=100, null=True, blank=True)
    rate = models.IntegerField(default=0)

    class Meta:
        db_table = 'user_lesson'
        verbose_name = 'user lesson'
        verbose_name_plural = 'user lessons'

    def __str__(self):
        return '{user}-{lesson}'.format(user=self.user.auth_user.full_name, lesson=self.lesson.name)
