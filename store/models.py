from django.db import models

from feel_nigeria_backend import settings

# Create your models here.

class Customer(models.Model):
    company = models.CharField(max_length=255)
    phone_number = models.CharField(
        max_length=255, null=True, )
    nationality = models.CharField(
        max_length=255, null=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    preferred_destination = models.CharField(max_length=255, null=True)
    travel_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.user.name
