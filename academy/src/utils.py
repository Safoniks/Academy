import hashlib
from django.utils.crypto import get_random_string
from django.conf import settings
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template


def generate_confirmation_code(email):
    secret_key = get_random_string()
    qqq = hashlib.sha256((secret_key + email).encode('utf-8')).hexdigest()
    print(qqq)
    return hashlib.sha256((secret_key + email).encode('utf-8')).hexdigest()


def send_confirmation_email(user):
    plaintext = get_template('academy_site/inclusion/confirmation_email.txt')
    htmly = get_template('academy_site/inclusion/confirmation_email.html')

    link = reverse('academy_site:email_confirm', kwargs={
        'user_id': user.pk,
        'code': user.siteuser.confirmation_code,
    })
    context = {
        'full_name': user.full_name,
        'link': 'http://' + settings.HOST + ':8000' + link,
    }

    subject, from_email, to = settings.CONFIRMATION_EMAIL_SUBJECT, settings.DEFAULT_FROM_EMAIL, user.email
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
