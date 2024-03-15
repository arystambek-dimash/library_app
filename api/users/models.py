from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    ADMIN = 1
    CLIENT = 2

    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (CLIENT, 'Client')
    )

    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=CLIENT)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    name = models.CharField(max_length=32)
    email = models.EmailField(max_length=100,
                              unique=True,
                              verbose_name='email address',
                              null=False,
                              error_messages={
                                  "unique": "A user with that email already exists.",
                              },
                              )
    password = models.CharField(max_length=128)
    role = models.ForeignKey(Role, on_delete=models.DO_NOTHING, default=2)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'password']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
