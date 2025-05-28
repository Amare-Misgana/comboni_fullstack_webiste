from django.db import models
from common.models import CustomUser


class TeacherAction(models.Model):
    teacher = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, related_name="teacher"
    )
    action = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)
