from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model

from academy_site.models import SiteUser
AuthUser = get_user_model()


@receiver(post_save, sender=AuthUser)
def create_site_user(sender, instance, created, **kwargs):
    if created and instance.is_site_user:
        new_site_user = SiteUser(auth_user=instance)
        new_site_user.save()


@receiver(post_delete, sender=SiteUser)
def delete_site_user(sender, instance, **kwargs):
    if hasattr(instance, 'user'):
        instance.user.delete()
