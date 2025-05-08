from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import HttpResponse
from .models import AdminAction
import pandas as pd
from common.models import UserProfile, CustomUser, ClassRoom
import openpyxl
import secrets
import string
from io import BytesIO
import re

# ==================  HOME ==================

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def school_admin_dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    students_amount = CustomUser.objects.filter(role="student").count()
    teachers_amount = CustomUser.objects.filter(role="teacher").count()
    admin_actions = AdminAction.objects.select_related('admin').all().order_by('-timestamp')
    admin_profiles = UserProfile.objects.all()
    
    context = {
        "user_profile": user_profile,
        "students_amount": students_amount,
        "teachers_amount": teachers_amount,
        "grades_amount": 23,
        "sections_amount": 23,
        "admin_actions": zip(admin_actions, admin_profiles),
    }
    return render(request, "a_school_admin/dashboard.html", context)

# =================== Students View =================











@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def materials(request):
    pass



teacher_excel = {}







