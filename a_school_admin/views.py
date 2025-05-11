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
    students_amount = CustomUser.objects.filter(role="student").count()
    teachers_amount = CustomUser.objects.filter(role="teacher").count()
    sections = Class.objects.all().count()
    admin_actions = AdminAction.objects.select_related('admin').all().order_by('-timestamp')
    admin_profiles = UserProfile.objects.all()

    classes = sorted(set(int(item[:-1]) for item in Class.objects.values_list("class_name", flat=True)))


    grades = classes
    gender_data = {grade: {'male': 0, 'female': 0} for grade in grades}

    for classroom in ClassRoom.objects.all():
        grade = ''.join(filter(str.isdigit, classroom.class_name.class_name))
        if grade in gender_data:
            students = classroom.students.filter(role='student')
            for student in students:
                if student.gender in ['male', 'female']:
                    gender_data[grade][student.gender] += 1
    
    context = {
        "user_profile": user_profile,
        "students_amount": students_amount,
        "teachers_amount": teachers_amount,
        "classes_amount": len(classes),
        "sections_amount": sections,
        "classes": classes,
        "admin_actions": zip(admin_actions, admin_profiles),
        'labels': [f'Grade {g}' for g in grades],
        'male_data': [gender_data[g]['male'] for g in grades],
        'female_data': [gender_data[g]['female'] for g in grades],
    }
    return render(request, "a_school_admin/dashboard.html", context)

# =================== Students View =================











@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def materials(request):
    pass



teacher_excel = {}







