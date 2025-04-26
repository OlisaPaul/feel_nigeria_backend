from django.contrib.auth.models import AbstractUser
from django.db import models

class CUser(AbstractUser):
    name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(unique=True, blank=True)