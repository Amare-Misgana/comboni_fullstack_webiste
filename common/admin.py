from django.contrib import admin
from .models import Message, CustomUser, UserProfile


admin.site.register([Message, CustomUser, UserProfile])
