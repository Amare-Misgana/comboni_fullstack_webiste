from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponse
from a_school_admin.models import AdminAction
import pandas as pd
from common.models import UserProfile, CustomUser, ClassRoom, Class
from django.db.models.functions import Length
import openpyxl
import secrets
import string
from io import BytesIO
import re







# ===================  Classes View ==================

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def class_mang(request):
    context = {
        "classes": Class.objects.all().order_by(Length('class_name'), 'class_name')
    }
    # waiting classes and class_performance
    return render(request, "a_school_admin/class-mang.html", context)

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_class(request, class_name):
    context = {

    }
    # waiting class_info
    return render(request, "a_school_admin/edit-class.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def class_detial(request, class_name): 
    context = {

    }
    #, waiting class_info
    return render(request, "a_school_admin/class-detail.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_class(request):
    try:
        teachers_in_userprofile = CustomUser.objects.filter(customuser__role='teacher')
        teachers_in_classroom = ClassRoom.objects.values_list("room_teacher", flat=True)
        teachers_not_in_classroom = teachers_in_userprofile.exclude(customuser__id__in=teachers_in_classroom)
    except Exception as e:
        messages.error(request, "Failed to load teacher data. Please try again.")
        return render(request, "a_school_admin/class-mang.html")

    try:
        students_in_userprofile = UserProfile.objects.filter(customuser__role='student')
        students_in_classroom_ids = ClassRoom.objects.values_list('student', flat=True)
        students_not_in_classroom = students_in_userprofile.exclude(customuser__id__in=students_in_classroom_ids)
    except Exception as e:
        messages.error(request, "Failed to load student data. Please try again.")
        return render(request, "a_school_admin/class-mang.html")

    try:
        classes_in_class_model = Class.objects.all()
        classes_in_classroom = ClassRoom.objects.values_list('class_room', flat=True)
        classes_not_in_classroom = classes_in_class_model.exclude(id__in=classes_in_classroom)
    except Exception as e:
        messages.error(request, "Failed to load class information. Please try again.")
        return render(request, "a_school_admin/class-mang.html")

    context = {
        'upload_title': "Add Students Via Excel",
        'students': students_not_in_classroom,
        'home_room_teachers': teachers_not_in_classroom,
        'classes': classes_not_in_classroom,
    }
    return render(request, "a_school_admin/add-class.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def create_classes(request):
    if request.method == 'POST':
        class_names_input = request.POST.get('class_names', '')
        
        # Process input
        raw_names = [name.strip() for name in class_names_input.split(',')]
        processed_names = []
        
        # Validate and standardize format (e.g., "11a" -> "11A")
        for name in raw_names:
            if not name:
                continue
                
            # Standardize format (digits followed by letter)
            match = re.match(r'^(\d+)([a-zA-Z])$', name)
            if match:
                grade = match.group(1)
                section = match.group(2).upper()
                standardized = f"{grade}{section}"
                processed_names.append(standardized)
            else:
                messages.warning(request, f"'{name}' is not a valid class format (e.g. 11A)")
        
        if not processed_names:
            messages.error(request, "No valid class names provided")
            return redirect('create_classes_url')
        
        # Check for existing classes
        existing_classes = set(Class.objects.filter(
            class_name__in=processed_names
        ).values_list('class_name', flat=True))
        
        new_classes = []
        duplicates = []
        
        for name in processed_names:
            if name in existing_classes:
                duplicates.append(name)
            else:
                new_classes.append(name)
        
        # Create new classes
        created = []
        for name in new_classes:
            Class.objects.create(class_name=name)
            created.append(name)
        
        # Prepare response
        context = {
            'duplicates': duplicates,
            'created': created,
            'input': class_names_input
        }
        
        if created:
            messages.success(request, f"Successfully created {len(created)} classes")
        if duplicates:
            messages.warning(request, f"{len(duplicates)} classes already exist")
        
        return render(request, 'a_school_admin/create-classes.html', context)  # Corrected template name
    
    return render(request, 'a_school_admin/create-classes.html')
