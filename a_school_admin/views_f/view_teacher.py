from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import HttpResponse
from a_school_admin.models import AdminAction
import pandas as pd
from common.models import UserProfile, CustomUser, ClassRoom
import openpyxl
from io import BytesIO
from a_school_admin.helper_func import validate_email, generate_password


# ===========================   Teachers View =====================



@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def teachers_mang(request):
    context = {
    }
    # waiting subjects and teachers
    return render(request, "a_school_admin/teachers-mang.html", context)

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_teacher(request):
    return render(request, "a_school_admin/add-teacher.html")


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_teacher(request, teacher_username):
    return render(request, "a_school_admin/edit-teacher.html")

def teacher_detail(request, teacher_username):
    print("\n\n\n\n", teacher_username)
    return render(request, "a_school_admin/teacher-detail.html")

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_teachers(request):
    if request.method == "POST" and request.FILES.get("file"):
        excel_file = pd.read_excel(request.FILES["file"])
        headers = excel_file.columns
        required_columns = ['first name', 'last name', 'middle name', 'email', 'age', 'phone number', 'gender', 'home room']

        for column in required_columns:
            if column not in headers:
                messages.error(request, f"'{column}' column is missing in the uploaded file.")
                return render(request, "a_school_admin/upload.html")

        for idx, row in excel_file.iterrows():
            if row.isnull().any():
                messages.error(request, f"Missing values in row {idx + 2}.")
                return render(request, "a_school_admin/upload.html")

            class_name = str(row['class']).replace(" ", "")
            grade = ''.join(filter(str.isdigit, class_name))
            section = ''.join(filter(str.isalpha, class_name))

            if not grade.isdigit() or int(grade) not in [9, 10, 11, 12]:
                messages.error(request, f"Invalid grade at line {idx + 2}: '{grade}'")
                return render(request, "a_school_admin/upload.html")

            if section.upper() not in "ABCDEFGH":
                messages.error(request, f"Invalid section at line {idx + 2}: '{section}'")
                return render(request, "a_school_admin/upload.html")

            if not ClassRoom.objects.filter(class_name=class_name).exists():
                messages.error(request, f"Invalid class name at line {idx + 2}: '{class_name}'")
                return render(request, "a_school_admin/upload.html")

            age = row['age']
            if not isinstance(age, (int, float)) or age < 4 or age > 80:
                messages.error(request, f"Invalid age at line {idx + 2}: '{age}'")
                return render(request, "a_school_admin/upload.html")

            phone_number = str(row['phone number'])
            if not phone_number.isdigit() or len(phone_number) != 10:
                messages.error(request, f"Invalid phone number at line {idx + 2}: '{phone_number}'")
                return render(request, "a_school_admin/upload.html")

            gender = str(row['gender']).upper()
            if gender not in ["M", "F"]:
                messages.error(request, f"Invalid gender at line {idx + 2}: '{gender}'")
                return render(request, "a_school_admin/upload.html")

            for name in [row['first name'], row['middle name'], row['last name']]:
                if not str(name).isalpha():
                    messages.error(request, f"Invalid name at line {idx + 2}: '{name}'")
                    return render(request, "a_school_admin/upload.html")

            email = str(row['email'])
            if not validate_email(email):
                messages.error(request, f"Invalid email at line {idx + 2}")
                return render(request, "a_school_admin/upload.html")

        for idx, row in excel_file.iterrows():
            password = generate_password()
            try:
                user = CustomUser.objects.create(
                    first_name=row['first name'],
                    middle_name=row['middle name'],
                    last_name=row['last name'],
                    email=row['email'],
                    gender="male" if row["gender"].upper() == "M" else "female",
                    phone_number=row["phone number"],
                    role="teacher"
                )
                user.set_password(password)
                user.save()

                UserProfile.objects.create(
                    user=user,
                    user_pic=row.get("pic", ""),
                    password=password
                )
            except Exception as e:
                messages.error(request, f"Error saving teacher: {str(e)}")
                return render(request, "a_school_admin/upload.html")

        messages.success(request, "Teachers added successfully.")
        return redirect("admin_dashboard_url")

    return render(request, "a_school_admin/upload.html")


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def download_student_excel(request):
    teachers = CustomUser.objects.filter(role="teacher")
    teacher_data = []
    for teacher in teachers:
        try:
            teacher_data.append({
                'first_name': teacher.first_name,
                'middle_name': teacher.middle_name,
                'last_name': teacher.last_name,
                'age': teacher.age,
                'room class': ClassRoom.objects.get(room_teacher=teacher).class_name,
                'email': teacher.email,
            })
        except:
            continue  # skip if class info is missing

    df = pd.DataFrame(teacher_data)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="teachers.xlsx"'
    return response