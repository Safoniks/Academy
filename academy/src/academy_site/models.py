import os
import uuid
from werkzeug.utils import secure_filename

from django.template.defaultfilters import slugify
from django.conf import settings
from django.db import models
from django.db.models import Q, Sum
from django.forms.models import model_to_dict
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.urls import reverse

from .validators import positive_number
from .choices import *


def get_image_path(instance, filename, dir_name):
    photo_name = str(uuid.uuid4()) + '.' + secure_filename(filename).rsplit('.', 1)[-1]
    return os.path.join(dir_name, photo_name)


class AuthUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save()
        return user

    def create_admin(self, email, password, profile_data=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Admin must have is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Admin must have is_admin=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Admin must have is_superuser=True.')
        auth_user = self._create_user(email, password, **extra_fields)
        profile_data = profile_data if profile_data else {}
        AdminProfile(auth_user=auth_user, **profile_data).save()
        return auth_user

    def create_moderator(self, email, password, profile_data=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Teacher must have is_staff=True.')
        if extra_fields.get('is_admin') is not True:
            raise ValueError('Admin must have is_admin=True.')
        auth_user = self._create_user(email, password, **extra_fields)
        profile_data = profile_data if profile_data else {}
        AdminProfile(auth_user=auth_user, **profile_data).save()
        return auth_user

    def create_teacher(self, email, password, profile_data=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Teacher must have is_staff=True.')
        auth_user = self._create_user(email, password, **extra_fields)
        profile_data = profile_data if profile_data else {}
        AdminProfile(auth_user=auth_user, **profile_data).save()
        return auth_user

    def create_site_user(self, email, password, profile_data=None, **extra_fields):
        if extra_fields.get('is_staff') is True:
            raise ValueError('Site user must have is_staff=False.')
        if extra_fields.get('is_admin') is True:
            raise ValueError('Site user must have is_admin=False.')
        if extra_fields.get('is_superuser') is True:
            raise ValueError('Site user must have is_superuser=False.')
        auth_user = self._create_user(email, password, **extra_fields)
        profile_data = profile_data if profile_data else {}
        SiteUser(auth_user=auth_user, **profile_data).save()
        return auth_user

    def admins(self, city=None):
        admin_queryset = self.filter(Q(is_admin=True) | Q(is_superuser=True))
        return admin_queryset.filter(city=city) if city else admin_queryset

    def teachers(self, city=None):
        teachers_queryset = self.filter(is_staff=True)
        return teachers_queryset.filter(city=city) if city else teachers_queryset

    def site_users(self):
        return self.filter(is_staff=False, is_admin=False, is_superuser=False)


def get_user_photo_path(*args):
    return get_image_path(*args, dir_name=settings.USER_PHOTOS_DIR_NAME)


class AuthUser(AbstractBaseUser, PermissionsMixin):
    RULES = {
        ADMINISTRATOR: {'is_superuser': True, 'is_admin': True, 'is_staff': True},
        MODERATOR: {'is_superuser': False, 'is_admin': True, 'is_staff': True},
        TEACHER: {'is_superuser': False, 'is_admin': False, 'is_staff': True},
        SITE_USER: {'is_superuser': False, 'is_admin': False, 'is_staff': False},
    }

    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to=get_user_photo_path, null=True, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False, blank=True)
    is_superuser = models.BooleanField(default=False)
    city = models.ForeignKey('City', on_delete=models.CASCADE, null=True, blank=True)
    USERNAME_FIELD = 'email'
    objects = AuthUserManager()

    class Meta:
        db_table = 'auth_user'
        verbose_name = 'authenticated user'
        verbose_name_plural = 'authenticated users'
        permissions = (
            ('some_perm', 'custom permission'),
        )

    def __str__(self):
        return self.email

    def get_admin_url(self):
        return reverse('academy_admin:user_detail', args=[str(self.pk)])

    def has_perm(self, perm, obj=None):
        try:
            user_perm = self.user_permissions.get(codename=perm)
        except ObjectDoesNotExist:
            user_perm = False
        return bool(user_perm)

    def save(self, *args, **kwargs):
        try:
            this = self.__class__.objects.get(pk=self.pk)
            if this.photo != self.photo:
                this.photo.delete(save=False)
        except:
            pass
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        ret = super(self.__class__, self).delete(*args, **kwargs)
        self.photo.delete(save=False)
        return ret

    @property
    def full_name(self):
        return '{first_name} {last_name}'.format(first_name=self.first_name, last_name=self.last_name)

    @property
    def is_site_user(self):
        for prop, value in self.RULES[SITE_USER].items():
            if getattr(self, prop, False) != value:
                return False
        return True

    @property
    def is_teacher(self):
        for prop, value in self.RULES[TEACHER].items():
            if getattr(self, prop, False) != value:
                return False
        return True

    @property
    def is_moderator(self):
        for prop, value in self.RULES[MODERATOR].items():
            if getattr(self, prop, False) != value:
                return False
        return True

    @property
    def is_administrator(self):
        for prop, value in self.RULES[ADMINISTRATOR].items():
            if getattr(self, prop, False) != value:
                return False
        return True

    def set_role(self, role):
        rules = self.RULES.get(role, None)
        if rules:
            for prop, value in rules.items():
                setattr(self, prop, value)

    def get_role(self):
        roles_dict = {
            'is_administrator': ADMINISTRATOR,
            'is_moderator': MODERATOR,
            'is_teacher': TEACHER,
            'is_site_user': SITE_USER,
        }
        for prop, value in roles_dict.items():
            if getattr(self, prop, False):
                return value

    def get_default_page(self):
        default_pages_dict = {
            'is_administrator': 'academy_admin:homepage',
            'is_moderator': 'academy_admin:cities',
            'is_teacher': 'academy_admin:courses',
            'is_site_user': 'academy_site:home',
        }
        for prop, value in default_pages_dict.items():
            if getattr(self, prop, False):
                return value

    def to_dict_info(self):
        fields = ['first_name', 'last_name', 'email', 'photo']
        return model_to_dict(self, fields=fields)


class SiteUser(models.Model):
    auth_user = models.OneToOneField('AuthUser', on_delete=models.CASCADE)
    birthdate = models.DateField(null=True, blank=True)
    phone = models.CharField(null=True, blank=True, max_length=20)
    country = models.CharField(null=True, blank=True, max_length=50)
    city = models.CharField(null=True, blank=True, max_length=50)
    address = models.CharField(null=True, blank=True, max_length=50)
    mother_language = models.CharField(null=True, blank=True, max_length=50)
    salutation = models.CharField(null=True, blank=True, max_length=50)
    know_academy_through = models.CharField(null=True, blank=True, max_length=200)
    postcode = models.IntegerField(null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    confirmation_code = models.CharField(max_length=64)
    confirmation_code_expires = models.DateTimeField()
    courses = models.ManyToManyField('Course', through='UserCourse')

    class Meta:
        db_table = 'site_user'
        verbose_name = 'site user'
        verbose_name_plural = 'site users'

    def to_dict_profile(self):
        fields_to_delete = ['auth_user', 'is_confirmed', 'confirmation_code', 'confirmation_code_expires', 'courses']
        return model_to_dict(self, exclude=fields_to_delete)

    def to_dict_user_info(self):
        return {**self.auth_user.to_dict_info(), **self.to_dict_profile()}

    def get_active_course_subscribes(self):
        return UserCourse.objects.active_entries().filter(user=self)

    def get_active_courses(self):
        return [subscribe.course for subscribe in self.get_active_course_subscribes()]


class AdminProfile(models.Model):
    auth_user = models.OneToOneField('AuthUser', on_delete=models.CASCADE)
    facebook_link = models.URLField(null=True, blank=True)
    instagram_link = models.URLField(null=True, blank=True)
    other_link = models.URLField(null=True, blank=True)
    phone = models.CharField(null=True, blank=True, max_length=20)
    bio = models.TextField(null=True, blank=True)
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'admin_profile'
        verbose_name = 'admin profile'
        verbose_name_plural = 'admin profiles'

    def save(self, *args, **kwargs):
        self.last_update = timezone.now()
        super(self.__class__, self).save(*args, **kwargs)


def get_partner_logo_path(*args):
    return get_image_path(*args, dir_name=settings.PARTNER_LOGOS_DIR_NAME)


class Partner(models.Model):
    name = models.CharField(max_length=20)
    link = models.URLField()
    logo = models.ImageField(upload_to=get_partner_logo_path)
    is_general = models.BooleanField()
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'partner'
        verbose_name = 'partner'
        verbose_name_plural = 'partners'

    def __str__(self):
        return self.name

    def get_admin_url(self):
        return reverse('academy_admin:partner_detail', args=[str(self.pk)])

    def save(self, *args, **kwargs):
        try:
            this = self.__class__.objects.get(pk=self.pk)
            if this.logo != self.logo:
                this.logo.delete(save=False)
        except:
            pass
        self.last_update = timezone.now()
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        ret = super(self.__class__, self).delete(*args, **kwargs)
        self.logo.delete(save=False)
        return ret


def get_city_photo_path(*args):
    return get_image_path(*args, dir_name=settings.CITY_PHOTOS_DIR_NAME)


class City(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(blank=True, unique=True)
    short_description = models.TextField()
    full_description = models.TextField()
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    photo = models.ImageField(upload_to=get_city_photo_path, null=True, blank=True)
    video = models.URLField(null=True, blank=True)
    location = models.CharField(max_length=100)
    last_update = models.DateTimeField(auto_now_add=True)
    partners = models.ManyToManyField('Partner')

    class Meta:
        db_table = 'city'
        verbose_name = 'city'
        verbose_name_plural = 'cities'

    def __str__(self):
        return self.name

    def get_admin_url(self):
        return reverse('academy_admin:city_detail', args=[str(self.pk)])

    def get_site_url(self):
        return reverse('academy_site:city_detail', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        try:
            this = self.__class__.objects.get(pk=self.pk)
            if this.photo != self.photo:
                this.photo.delete(save=False)
        except:
            pass
        self.last_update = timezone.now()
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        ret = super(self.__class__, self).delete(*args, **kwargs)
        self.photo.delete(save=False)
        return ret


def get_theme_photo_path(*args):
    return get_image_path(*args, dir_name=settings.THEME_PHOTOS_DIR_NAME)


class Theme(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to=get_theme_photo_path, null=True, blank=True)
    city = models.ForeignKey('City', on_delete=models.CASCADE)
    last_update = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'theme'
        verbose_name = 'theme'
        verbose_name_plural = 'themes'
        unique_together = (('city', 'slug',), ('city', 'name',))

    def __str__(self):
        return self.name

    def get_admin_url(self):
        return reverse('academy_admin:theme_detail', args=[str(self.pk)])

    def get_site_url(self):
        return reverse('academy_site:theme_detail', args=[str(self.city.slug), str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        try:
            this = self.__class__.objects.get(pk=self.pk)
            if this.photo != self.photo:
                this.photo.delete(save=False)
        except:
            pass
        self.last_update = timezone.now()
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        ret = super(self.__class__, self).delete(*args, **kwargs)
        self.photo.delete(save=False)
        return ret


def get_course_photo_path(*args):
    return get_image_path(*args, dir_name=settings.COURSE_PHOTOS_DIR_NAME)


class Course(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(blank=True)
    description = models.TextField()
    practise_info = models.TextField()
    location = models.CharField(max_length=100)
    photo = models.ImageField(upload_to=get_course_photo_path)
    price = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    price_description = models.CharField(max_length=100, null=True, blank=True)
    seats = models.IntegerField(validators=[positive_number])
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    theme = models.ForeignKey('Theme', on_delete=models.CASCADE)
    partners = models.ManyToManyField('Partner')
    teachers = models.ManyToManyField('AuthUser')

    class Meta:
        db_table = 'course'
        verbose_name = 'course'
        verbose_name_plural = 'courses'
        unique_together = (('theme', 'slug',), ('theme', 'name',))

    def __str__(self):
        return self.name

    @property
    def next_lesson(self):
        return self.lesson_set.filter(date__gt=timezone.now()).first()

    @property
    def remaining_seats(self):
        return self.seats - UserCourse.objects.active_entries().filter(course=self).count()

    @property
    def reserved_seats(self):
        return self.seats - self.remaining_seats

    @property
    def is_sold_out(self):
        return self.remaining_seats < 1

    @property
    def is_archived(self):
        last_lesson = self.lesson_set.all().last()
        if last_lesson:
            return last_lesson.date < timezone.now()
        return False

    @property
    def rate(self):
        return UserCourse.objects.ratio_like_dislike(self)

    def get_active_subscriber_records(self):
        return UserCourse.objects.active_entries().filter(course=self)

    def get_active_subscribers_info(self):
        subscribers = []
        for user_course in self.get_active_subscriber_records():
            if user_course.user:
                user_info = user_course.user.to_dict_user_info()
                user_info['is_anonymous'] = False
            else:
                user_info = model_to_dict(user_course.anonymous)
                user_info['is_anonymous'] = True
            user_info['is_confirmed'] = user_course.is_confirmed
            user_info['subscribe_date'] = user_course.date
            subscribers.append(user_info)
        return subscribers

    def get_admin_url(self):
        return reverse('academy_admin:course_detail', args=[str(self.pk)])

    def get_site_url(self):
        return reverse('academy_site:course_detail',
                       args=[str(self.theme.city.slug), str(self.theme.slug), str(self.slug)])

    def get_signup_url(self):
        return reverse('academy_site:signup_course',
                       args=[str(self.theme.city.slug), str(self.theme.slug), str(self.slug)])

    def get_unsubscribe_url(self):
        return reverse('academy_site:unsubscribe_course',
                       args=[str(self.theme.city.slug), str(self.theme.slug), str(self.slug)])

    def get_like_url(self):
        return reverse('academy_site:like_course',
                       args=[str(self.theme.city.slug), str(self.theme.slug), str(self.slug)])

    def get_dislike_url(self):
        return reverse('academy_site:dislike_course',
                       args=[str(self.theme.city.slug), str(self.theme.slug), str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = slugify(self.name)
        try:
            this = self.__class__.objects.get(pk=self.pk)
            if this.photo != self.photo:
                this.photo.delete(save=False)
        except:
            pass
        super(self.__class__, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        ret = super(self.__class__, self).delete(*args, **kwargs)
        self.photo.delete(save=False)
        return ret


class Lesson(models.Model):
    date = models.DateTimeField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    class Meta:
        db_table = 'lesson'
        verbose_name = 'lesson'
        verbose_name_plural = 'lessons'
        ordering = ['date']

    @property
    def is_past(self):
        return self.date < timezone.now()


class UserCourseManager(models.Manager):
    def active_entries(self):
        return self.get_queryset().filter(
            (Q(is_confirmed=True) | Q(confirmation_code_expires__gt=timezone.now())) & Q(is_unsubscribed=False)
        )

    def likes(self, course):
        return self.active_entries().filter(vote__gt=0, course=course)

    def dislikes(self, course):
        return self.active_entries().filter(vote__lt=0, course=course)

    def ratio_like_dislike(self, course):
        likes_count = self.likes(course).count()
        dislikes_count = self.dislikes(course).count()
        try:
            ratio = (likes_count / (likes_count + dislikes_count)) * 100
        except ZeroDivisionError:
            return 0
        return round(ratio, 2)


class UserCourse(models.Model):
    LIKE = 1
    DISLIKE = -1

    VOTES = (
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like')
    )

    user = models.ForeignKey('SiteUser', on_delete=models.CASCADE, null=True, blank=True)
    anonymous = models.OneToOneField('Anonymous', on_delete=models.CASCADE, null=True, blank=True)
    course = models.ForeignKey('Course', on_delete=models.CASCADE)
    questions = models.CharField(max_length=100)
    vote = models.SmallIntegerField(choices=VOTES, default=0)
    date = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    confirmation_code = models.CharField(max_length=64)
    confirmation_code_expires = models.DateTimeField()
    count = models.IntegerField(default=1)
    is_unsubscribed = models.BooleanField(default=False)

    objects = UserCourseManager()

    class Meta:
        db_table = 'user_course'
        verbose_name = 'user course'
        verbose_name_plural = 'user courses'
        unique_together = ('user', 'course',)

    def __str__(self):
        return '{user}-{course}'.format(user=self.user.auth_user.full_name, course=self.course.name)

    @property
    def is_liked(self):
        return self.vote == self.LIKE

    @property
    def is_disliked(self):
        return self.vote == self.DISLIKE

    def get_user_attr(self, attr, default=None):
        if self.anonymous:
            return getattr(self.anonymous, attr, default)

        value = getattr(self.user, attr, default)
        if value is not default:
            return value
        else:
            return getattr(self.user.auth_user, attr, default)


class Anonymous(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    birthdate = models.DateField()
    phone = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    mother_language = models.CharField(max_length=50)
    salutation = models.CharField(max_length=50)
    know_academy_through = models.CharField(max_length=200)
    postcode = models.IntegerField()

    class Meta:
        db_table = 'anonymous'
        verbose_name = 'anonymous'
        verbose_name_plural = 'anonymous'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return '{first_name} {last_name}'.format(first_name=self.first_name, last_name=self.last_name)
