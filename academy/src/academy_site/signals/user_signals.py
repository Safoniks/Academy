from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from academy_site.models import SiteUser, Teacher
AuthUser = get_user_model()


@receiver(post_save, sender=AuthUser)
def create_site_user(sender, instance, created, **kwargs):
    if created and instance.is_site_user:
        new_site_user = SiteUser(auth_user=instance)
        new_site_user.save()


@receiver(post_delete, sender=SiteUser)
def delete_site_user(sender, instance, **kwargs):
    if hasattr(instance, 'auth_user'):
        instance.auth_user.delete()


@receiver(post_save, sender=AuthUser)
def create_teacher(sender, instance, created, **kwargs):
    if created and instance.is_teacher:
        new_teacher = Teacher(auth_user=instance)
        new_teacher.save()


@receiver(post_delete, sender=SiteUser)
def delete_teacher(sender, instance, **kwargs):
    if hasattr(instance, 'auth_user'):
        instance.auth_user.delete()
