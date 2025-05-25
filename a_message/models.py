from django.db import models
from common.models import UserProfile, CustomUser

class Message(models.Model):
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.receiver} at {self.timestamp}"
    
class OnlineStatus(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    online_status = models.BooleanField(default=False)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} is {'online' if self.online_status else 'offline'}"