from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class CUser(models.Model):
    firstName = models.TextField(max_length=20)
    lastName = models.TextField(max_length=20)
    username = models.TextField(unique=True, primary_key=True)
    streamNames = models.TextField(max_length=10000)
    password = models.CharField(max_length=1000)
    dateCreated = models.DateField(auto_now=True)
    subscription = models.IntegerField(default=3)
    streamID = models.TextField(default="null")
    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)