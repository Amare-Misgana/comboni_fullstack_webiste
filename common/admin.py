from django.contrib import admin
from .models import CustomUser, UserProfile, Class, ClassRoom, ClassSubject
from a_message.models import Message


admin.site.register([Message, CustomUser, UserProfile, Class, ClassRoom, ClassSubject])
