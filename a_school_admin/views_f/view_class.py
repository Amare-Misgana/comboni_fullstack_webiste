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
        "classes": Class.objects.all().order_by(Length('class_name'), 'class_name'),
        "class_rooms": ClassRoom.objects.all()
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
        teachers_not_in_classroom = UserProfile.objects.filter(
            user__role='teacher'
        ).exclude(
            user__id__in=ClassRoom.objects.values_list("room_teacher", flat=True)
        )
        if not teachers_not_in_classroom:
            messages.warning(request, "You don't have any teachers stored in the system!")
            return redirect("class_mang_url")
    except Exception as e:
        messages.error(request, "Failed to load teacher data. Please try again.")
        return redirect("class_mang_url")


    try:
        students_not_in_classroom = UserProfile.objects.filter(
            user__role='student'
        ).exclude(
            user__id__in=ClassRoom.objects.values_list('student', flat=True)
        )
        if not students_not_in_classroom:
            messages.warning(request, "You don't have any studetns stored in the system!")
            return redirect("class_mang_url")
    except Exception as e:
        messages.error(request, "Failed to load student data. Please try again.")
        return redirect("class_mang_url")

    try:
        classes_not_in_classroom = Class.objects.exclude(
            id__in=ClassRoom.objects.values_list('class_name', flat=True)
        )
        if not classes_not_in_classroom:
            messages.warning(request, "You don't have any classes stored in the stystem!")
            return redirect("class_mang_url")
    except Exception:
        messages.error(request, "Failed to load class information. Please try again.")
        return redirect("class_mang_url")

    context = {
        'students': students_not_in_classroom,
        'home_room_teachers': teachers_not_in_classroom,
        'classes': classes_not_in_classroom,
    }
    return render(request, "a_school_admin/add-class.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def create_classes(request):
    if request.method == 'POST':
        class_names_input = request.POST.get('class_names', '')
        raw_names = [name.strip() for name in class_names_input.split(',') if name.strip()]
        processed_names = []

        for name in raw_names:
            match = re.match(r'^(\d+)([a-zA-Z])$', name)
            if match:
                grade = match.group(1)
                section = match.group(2).upper()
                processed_names.append(f"{grade}{section}")
            else:
                messages.warning(request, f"'{name}' is not a valid class format (e.g. 11A)")

        if not processed_names:
            messages.error(request, "No valid class names provided.")
            return redirect('create_classes_url')

        unique_names = set(processed_names)

        existing = set(Class.objects.filter(
            class_name__in=unique_names
        ).values_list('class_name', flat=True))

        new_classes = [name for name in unique_names if name not in existing]
        duplicates = [name for name in unique_names if name in existing]

        for name in new_classes:
            Class.objects.create(class_name=name)

        if new_classes:
            messages.success(request, f"Successfully created {len(new_classes)} classes.")
        if duplicates:
            messages.warning(request, f"{len(duplicates)} classes already exist: {', '.join(duplicates)}")

        return render(request, 'a_school_admin/create-classes.html', {
            'classes': Class.objects.all()
        })

    return render(request, 'a_school_admin/create-classes.html', {
        'classes': Class.objects.all().order_by(Length('class_name'), 'class_name')
    })

@user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
def class_detail(request, class_name):
    try:
        class_name = get_object_or_404(Class, class_name=class_name)
        class_room = get_object_or_404(ClassRoom, class_name=class_name)
        if class_room.class_name:
            messages.error(request, "Empty class name")
        students = list(class_room.students.all())
    except Exception as e:
        messages.error(request, f"Error quering data from the database: {e}")
        return redirect("class_mang_url")

    context = {
        "students": students,
        "class_room": class_room,
    }
    return render(request, 'a_school_admin/class-detail.html', context)

@user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
def edit_class(request, class_name):
    pass


@user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
def defined_class(request, defined_class_room):
    pass