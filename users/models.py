from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField(unique=True)

    def __str__(self):
        return f"{self.user.username} (TG ID: {self.telegram_id})"
