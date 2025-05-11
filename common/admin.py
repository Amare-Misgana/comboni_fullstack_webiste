from django.contrib import admin
from .models import Message, CustomUser, UserProfile, Class, ClassRoom, ClassSubject


admin.site.register([Message, CustomUser, UserProfile, Class, ClassRoom, ClassSubject])
