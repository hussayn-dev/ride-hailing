import time

from django.conf import settings
from django.core.files import File
from django.core.mail import EmailMultiAlternatives
from django.utils.crypto import get_random_string


def send_email(subject, email_from, html_alternative, text_alternative):
    msg = EmailMultiAlternatives(
        subject, text_alternative, settings.EMAIL_FROM, [email_from]
    )
    msg.attach_alternative(html_alternative, "text/html")
    msg.send()


async def create_file_from_image(url):
    return File(open(url, "rb"))


def generate_token(user):
    return get_random_string(120) + str(user.id) + str(time.time())[:6]
