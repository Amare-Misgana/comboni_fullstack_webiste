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
import openpyxl
import secrets
import string
from io import BytesIO
import re







# ===================  Classes View ==================

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def class_mang(request):
    context = {

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

    teachers_in_userprofile = CustomUser.objects.filter(customuser__role='teacher')
    teachers_in_classroom = ClassRoom.objects.values_list("room_teacher", flat=True)
    teachers_not_in_classroom = teachers_in_userprofile.exclude(customuser__id__in=teachers_in_classroom)

    students_in_userprofile = UserProfile.objects.filter(customuser__role='student')
    students_in_classroom_ids = ClassRoom.objects.values_list('student', flat=True)
    students_not_in_classroom = students_in_userprofile.exclude(customuser__id__in=students_in_classroom_ids)

    classes_in_class_model = Class.objects.all()
    classes_in_classroom = ClassRoom.objects.values_list('class_room', flat=True)
    classes_not_in_classroom = classes_in_class_model.exclude(id__in=classes_in_classroom)

    context = {
        'upload_title': "Add Students Via Excel",
        'students': students_not_in_classroom,
        'home_room_teachers': teachers_not_in_classroom,
        'classes': classes_not_in_classroom,
    }
    return render(request, "a_school_admin/add-class.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")

