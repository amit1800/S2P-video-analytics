from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from multiselectfield import MultiSelectField
import uuid
MODEL_CHOICES = (("human", "human"), ("fire", "fire"), ("weapon", "weapon"), ("numberplate", "numberplate"))

class CUser(models.Model):
    firstName = models.TextField(max_length=20)
    lastName = models.TextField(max_length=20)
    username = models.TextField(unique=True, primary_key=True)
    password = models.CharField(max_length=1000)
    dateCreated = models.DateField(auto_now=True)
    subscription = models.IntegerField(default=3)
    streamID = models.TextField(default="null")
    active_models = MultiSelectField(choices=MODEL_CHOICES, max_choices=4, max_length=2048, default=None)
    def __str__(self):
        return self.username
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)

class Track(models.Model):
    name = models.TextField()
    date_time = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)
    uuid = models.UUIDField( default=uuid.uuid4, editable=False)
    cuser = models.ForeignKey(CUser, on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    
class Detection(models.Model):
    type = MultiSelectField(choices=MODEL_CHOICES, max_choices=4, max_length=2048, default=None)
    # track = models.ForeignKey(Track, on_delete=models.CASCADE)
    value = models.TextField(max_length=30)
    date_time = models.DateTimeField(auto_now=True)