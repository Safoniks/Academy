from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from academy_site.models import SiteUser, AdminProfile
AuthUser = get_user_model()


@receiver(post_delete, sender=SiteUser)
def delete_site_user(sender, instance, **kwargs):
    if hasattr(instance, 'auth_user'):
        instance.auth_user.delete()


@receiver(post_delete, sender=AdminProfile)
def delete_admin(sender, instance, **kwargs):
    if hasattr(instance, 'auth_user'):
        instance.auth_user.delete()
