from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class CustomUserManager(UserManager):
    ''' '''

    def get_logged(self):
        ''' '''
        return self.filter(logged_in=True).order_by('email')


class User(AbstractUser):
    ''' '''

    email = models.EmailField(unique=True)
    in_game = models.BooleanField(default=False)
    logged_in = models.BooleanField(default=False)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def get_status(self) -> str:
        ''' '''
        return 'Playing' if self.in_game else 'Available'
