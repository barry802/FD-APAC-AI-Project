from django.db import models
from django.contrib.auth.models import User

class BrianBot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    messageinput = models.TextField()
    bot_response = models.TextField()
    def __str__(self):
        return self.user.username    