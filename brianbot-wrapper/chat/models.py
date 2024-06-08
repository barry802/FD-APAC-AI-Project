from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    title = models.CharField(max_length=100)
    query = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="queries")