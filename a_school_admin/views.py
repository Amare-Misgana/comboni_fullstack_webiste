from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import HttpResponse
from .models import AdminAction
import pandas as pd
from common.models import UserProfile, CustomUser, ClassRoom, Class
import openpyxl
import secrets
import string
from io import BytesIO
import re

# ==================  HOME ==================

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def school_admin_dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    students = CustomUser.objects.filter(role="student")
    teachers = CustomUser.objects.filter(role="teacher")
    sections = Class.objects.all().count()
    admin_actions = AdminAction.objects.select_related('admin').all().order_by('-timestamp')
    admin_profiles = UserProfile.objects.select_related('user').all()

    action_profiles = []
    for action in admin_actions:
        profile = next((p for p in admin_profiles if p.user == action.admin), None)
        if profile:
            action_profiles.append((action, profile))

    classes = sorted(set(int(item[:-1]) for item in Class.objects.values_list("class_name", flat=True)))


    grades = {}

    for class_room in classes:
        grades[class_room] = {}
        grades[class_room]["male"] = students.filter(gender="male").count()
        grades[class_room]["female"] = students.filter(gender="female").count()
    
    context = {
        "user_profile": user_profile,
        "students_amount": students.count(),
        "teachers_amount": teachers.count(),
        "classes_amount": len(classes),
        "sections_amount": sections,
        "classes": classes,
        'action_profiles': action_profiles,
        'labels': [f'Grade {g}' for g in grades],
        'male_data': [grades[g]['male'] for g in grades],
        'female_data': [grades[g]['female'] for g in grades],
    }
    return render(request, "a_school_admin/dashboard.html", context)

# =================== Students View =================











@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def materials(request):
    pass



teacher_excel = {}







