from email.policy import default
from enum import unique
import uuid
from django.urls import reverse
from django.template.loader import render_to_string
from account import ACCOUNT
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import CustomUserManager
from django.utils.safestring import mark_safe
from django.core.mail import send_mail
from django.conf import settings


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    uid = models.UUIDField(default=uuid.uuid4)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    referral_code = models.CharField(max_length=50, null=True, blank=True)
    activation_key = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(null=True, blank=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def send_confirmation_email(self, request):
        if not self.is_active:
            location = reverse("activate_account", kwargs={"token": self.activation_key})
            link = request.build_absolute_uri(location)

            html_msg = render_to_string("registration/emails/email_confirmation.html", {'link': link})
            text_msg = render_to_string("registration/emails/email_confirmation.txt", {'link': link})
            email = send_mail(
                subject="Confirm Valid Account",
                message=text_msg,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.email,],
                html_message=html_msg,
                fail_silently=False
            )
            return email
        
    def get_active_referrals(self):
        return self.referrals.filter(is_active = True)