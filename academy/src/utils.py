import hashlib
from django.utils.crypto import get_random_string
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from django.contrib.auth import get_user_model
AuthUser = get_user_model()


def generate_confirmation_code(email):
    secret_key = get_random_string()
    return hashlib.sha256((secret_key + email).encode('utf-8')).hexdigest()


def send_confirmation_email(instance):
    plaintext = get_template('academy_site/inclusion/confirmation_email.txt')
    htmly = get_template('academy_site/inclusion/confirmation_email.html')

    if isinstance(instance, AuthUser):
        instance_data = {
            'id': instance.siteuser.pk,
            'email': instance.email,
            'full_name': instance.full_name,
            'confirmation_code': instance.siteuser.confirmation_code,
        }
    else:
        instance_data = {
            'id': instance.pk,
            'email': instance.get_user_attr('email'),
            'full_name': instance.get_user_attr('full_name'),
            'confirmation_code': instance.confirmation_code,
        }

    link = reverse('academy_site:email_confirm', kwargs={
        'instance_id': instance_data['id'],
        'code': instance_data['confirmation_code'],
    })
    context = {
        'full_name': instance_data['full_name'],
        'link': 'http://' + settings.HOST + ':8000' + link,
    }

    subject, from_email, to = settings.CONFIRMATION_EMAIL_SUBJECT, settings.DEFAULT_FROM_EMAIL, instance_data['email']
    text_content = plaintext.render(context)
    html_content = htmly.render(context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_reset_password_email(user, new_password):
    plaintext = get_template('academy_site/inclusion/reset_password.txt')
    htmly = get_template('academy_site/inclusion/reset_password.html')

    context = {
        'full_name': user.full_name,
        'new_password': new_password,
    }

    subject, from_email, to = settings.RESET_PASSWORD_SUBJECT, settings.DEFAULT_FROM_EMAIL, user.email
    text_content = plaintext.render(context)
    html_content = htmly.render(context)
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
