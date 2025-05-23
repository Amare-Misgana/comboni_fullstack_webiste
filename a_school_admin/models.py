from django.db import models
from common.models import CustomUser


class AdminAction(models.Model):
    admin = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="admin")
    action = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)


class News(models.Model):
    photo = models.ImageField(upload_to='news_photos/')
    header = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)