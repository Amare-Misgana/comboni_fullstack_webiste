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
import json

# ==================  HOME ==================

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def school_admin_dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    
    students = CustomUser.objects.filter(role="student")
    teachers = CustomUser.objects.filter(role="teacher")
    classes = sorted(set(int(item[:-1]) for item in Class.objects.values_list("class_name", flat=True)))
    classrooms = ClassRoom.objects.select_related('class_name', 'room_teacher').prefetch_related('students')
    
    grades = {}
    for classroom in classrooms:
        class_students = classroom.students.all()
        grades[classroom.class_name.class_name] = {
            "male": class_students.filter(gender="male").count(),
            "female": class_students.filter(gender="female").count()
        }
    
    classes_json = {
        "classes": [str(classroom.class_name) for classroom in classrooms],
        "data": [{
            "class": str(classroom.class_name),
            "male": grades[str(classroom.class_name)]["male"],
            "female": grades[str(classroom.class_name)]["female"]
        } for classroom in classrooms]
    }
    admin_actions = AdminAction.objects.select_related('admin').all().order_by('-timestamp')
    admin_profiles = UserProfile.objects.select_related('user').all()

    action_profiles = []
    for action in admin_actions:
        profile = next((p for p in admin_profiles if p.user == action.admin), None)
        if profile:
            action_profiles.append((action, profile))

    context = {
        "user_profile": user_profile,
        "students_amount": students.count(),
        "teachers_amount": teachers.count(),
        "classes_amount": len(classes),
        "sections_amount": classrooms.count(),  # Since ClassRoom is the section
        "classes": sorted({classroom.class_name.class_name[:-1] for classroom in classrooms}),  # Extract grade levels
        'action_profiles': action_profiles,  # Implement your action profiles logic
        "gender_json": json.dumps(grades),
        "class_json": json.dumps(classes_json)
    }
    
    return render(request, "a_school_admin/dashboard.html", context)

# =================== Students View =================











@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def materials(request):
    pass



teacher_excel = {}







