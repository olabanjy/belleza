from django.db import models
from core.models import BaseAbstractModel
from django.conf import settings
import random, string
from django.db.models.signals import post_save
from django.utils.translation import gettext_lazy as _
from . import choices

# Create your models here.


class Profile(BaseAbstractModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_code = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=40, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    first_name = models.CharField(blank=True, null=True, max_length=200)
    last_name = models.CharField(blank=True, null=True, max_length=200)
    dob = models.DateField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=200, blank=True, null=True)
    welcome_email = models.CharField(max_length=100, default="pending")
    user_type = models.TextField(
        choices=choices.USER_TYPE_CHOICES,
        default=choices.UserType.Client.value,
        verbose_name=_("user_type"),
    )

    def __str__(self):
        return self.user.email

    @property
    def last_login(self, *args, **kwargs):
        the_last_login = self.user.last_login
        if the_last_login:
            user_last_login = the_last_login.strftime("%Y-%m-%d %H:%M")
            return user_last_login
        return None


def profile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        profile = Profile.objects.get_or_create(user=instance)

    profile, created = Profile.objects.get_or_create(user=instance)

    if profile.user_code is None or profile.user_code == "":
        profile.user_code = str(
            "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        )
        profile.save()


post_save.connect(profile_receiver, sender=settings.AUTH_USER_MODEL)
