from django.core import mail
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from api_yamdb.settings import DEFAULT_FROM_EMAIL


def email_is_valid(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def generate_mail(to_email, code):
    subject = 'Confirmation code для YaMDB'
    to = to_email
    text_content = f'''Вы запросили подтверждение регистрации
                       для работы с API YaMDB {code}'''
    mail.send_mail(
        subject, text_content,
        DEFAULT_FROM_EMAIL, [to],
        fail_silently=False
    )
