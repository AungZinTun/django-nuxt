from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import managers


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField()
    gender = models.CharField(
        max_length=140,
        null=True,
        choices=(
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other')
        )
    )
    birth_date = models.DateField(null=True, blank=True)
    pro = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = managers.CustomUserManager()

    def __str__(self):
        return self.email
