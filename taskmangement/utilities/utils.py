import random
from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4
import uuid
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.core.validators import RegexValidator, validate_email
from django.db import models
from django.db.models import QuerySet, Subquery
from django.utils.translation import gettext_lazy as _
from config.settings.base import EMAIL_HOST_USER


def generate_id(length: int = 10):
    """generate id for all the models

    Args:
        length (int, optional): _description_. Defaults to 10.

    Returns:
        _type_: _description_
    """
    return uuid4().hex[:length]


def generate_unique_random_password(name, email):
    return make_password(f"{name}{email}")


def send_otp_by_mail(email):
    # from argue_football.users.models import User as user
    """This send otp to user's email during registeration

    Args:
        otp (_type_): _description_
        email (_type_): _description_
    """

    # otp = OTP
    subject = "Email Verification"
    message = f"Your registeration is successfull, Please change your password"

    send_mail(subject, message, from_email=EMAIL_HOST_USER, recipient_list=[email], fail_silently=True)


def new_account_password_prompt(email, name, password):
    subject = 'Your New Account Information'
    message = f"""
                Hello {name},Your temporary password is: {password},
                Please click the link below to reset your password:
                http://0.0.0.0:8000/task_mangement/v1/password_reset/
                You should change your password as soon as possible.
    
            """
    send_mail(subject, message, from_email=EMAIL_HOST_USER, recipient_list=[email], fail_silently=True)



phone_regex_check = RegexValidator(regex=r"^\d{10}$", message="Phone number must be 10 digits only")
email_validator = validate_email
OTP_MAX_TRY = 3
MIN_PASSWORD_LENGTH = 8
OTP = random.randint(1000, 9999)
OPT_EXPIRE = datetime.now() + timedelta(minutes=1)


class BaseModelMixin(models.Model):
    id = models.CharField(primary_key=True, default=generate_id, editable=False, max_length=255)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False, db_index=True)
    active = models.BooleanField(_("active"), default=True, db_index=True)

    def __str__(self):
        return f"< {type(self).__name__}({self.id}) >"

    @classmethod
    def _serializer_fields(cls, exclude=[], *args):
        args = ["id", "active", *args, "created_at", "updated_at"]
        return sorted(list({field for field in args if field and field not in exclude}))

    @classmethod
    def _serializer_extra_kwargs(cls, exclude=[], **kwargs: dict[str, Any]):
        return {key: value for key, value in kwargs.items() if value and key not in exclude}

    @classmethod
    def serializer_fields(cls, *args, exclude=[]):
        return cls._serializer_fields(exclude, *args)

    @classmethod
    def serializer_extra_kwargs(cls, exclude=[], **kwargs):
        return cls._serializer_extra_kwargs(exclude, **kwargs)

    class Meta:
        abstract = True
        ordering = ["-created_at"]


def get_field_null_kargs(exclude: list[str] = [], **kwargs):
    _kwargs = {"null": True, "blank": True, "default": None, **kwargs}

    result = {}
    for key, value in _kwargs.items():
        if key not in exclude:
            result[key] = value

    return result


def make_distinct(qs: QuerySet, field: str = "id") -> QuerySet:
    """function generate unique queryset using subquery

    Args:
        qs (QuerySet): description
        field (str, optional): description. Defaults to "id".

    Returns:
        QuerySet: description
    """
    kwargs = {f"{field}__in": Subquery(qs.values(field))}
    return qs.model.objects.filter(**kwargs)

class Urgency_Level(models.TextChoices):
    HIGH = "HIGH", _("High")
    URGENT = "URGENT", _("Urgent")
    CRITICAL = "CRITICAL", _("Critical")
    ASAP = "ASAP", _("Asap")
    

class Status(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    STARTED = "STARTED", _("Started")
    ONGOING = "ONGOING", _("Ongoing")
    STUCK = "STUCK", _("Stuck")
    COMPLETED = "COMPLETED", _("Completed")
    