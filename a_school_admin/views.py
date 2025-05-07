from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
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

@login_required
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


@login_required
def students_mang(request):
    User = get_user_model()
    students = User.objects.filter(role='student')
    context = {
        "students": students,
    }
    return render(request, "a_school_admin/students-mang.html", context)

@login_required
def edit_student(request, student_username):
    Student = get_user_model()
    student = Student.objects.get(username=student_username)
    print(student)
    student_profile = get_object_or_404(UserProfile, user=student)

    if request.method == 'POST':
        try:
            student.first_name = request.POST.get('first_name')
            student.middle_name = request.POST.get('middle_name', '')
            student.last_name = request.POST.get('last_name')
            student.phone_number = request.POST.get('phone_number')
            student.age = request.POST.get('age')
            student.email = request.POST.get('email')

            password = request.POST.get('password')
            if password:
                student.set_password(password) 
                student_profile.password = password 

            profile_image = request.FILES.get('profile_image')
            if profile_image:
                student_profile.user_pic = profile_image

            student.save()
            student_profile.save() 

            # Admin action 

            admin_action = AdminAction(
                admin = request.user,
                action = f"Edited User ({student.first_name})"
            )
            admin_action.save()

            messages.success(request, 'Student added successfully.')
            return redirect('students_mang_url')
        
        except Exception as e:
            messages.error(request, f"Update failed: {str(e)}")
        
    context = {
        "student_profile": student_profile
    }
    return render(request, "a_school_admin/edit-students.html", context)

@login_required
def add_student(request):
    if request.method == 'POST':
        student = None
        try:
            first_name = request.POST.get("first_name")
            middle_name = request.POST.get("middle_name")
            last_name = request.POST.get("last_name")
            phone_number = request.POST.get("phone_number")
            age = request.POST.get("age")
            gender = request.POST.get("gender")
            password = request.POST.get('password')
            profile_pic = request.FILES.get("profile_pic")
            if password:
                student = CustomUser(
                    first_name = first_name,
                    middle_name = middle_name,
                    last_name = last_name,
                    phone_number = phone_number,
                    age = age,
                    gender = gender,  
                )
                student.set_password(password)
                student.save()
                
                student_profile = UserProfile (
                    user = student,
                    user_pic = profile_pic,
                )
                student_profile.save()
            else:
                messages.error(request, "Password can't be empty!")
                return redirect(reverse("students_mang_url"))
            # Admin action 
            admin_action = AdminAction(
                admin = request.user,
                action = f"Added User ({student.first_name})"
            )
            admin_action.save()
            messages.success(request, 'Student updated successfully.')
            return redirect('students_mang_url')
        except Exception as e:
            messages.error(request, f"Update failed: {str(e)}")
        return redirect(reverse("students_mang_url"))
    return render(request, "a_school_admin/add-student.html")

@login_required
def student_detail(request, student_username):
    Student = get_user_model()
    try:
        student = Student.objects.get(username=student_username)
        try:
            student_profile = UserProfile.objects.get(user=student)
        except UserProfile.DoesNotExist:
            messages.warning(request, "Student Profile is incomplete. Compelete Profile")
            return redirect(reverse("edit_student_url", kwargs={"student_username":student_username}))

    except Student.DoesNotExist:
        messages.error(request, "Student can't be found!")
        return redirect(reverse("student_mang_url"))
    context = {
        "student": student,
        "student_profile": student_profile,
    }
    return render(request, "a_school_admin/student-detail.html", context)



# ===================  Classes View ==================

@login_required
def class_mang(request):
    context = {

    }
    # waiting classes and class_performance
    return render(request, "a_school_admin/class-mang.html", context)

@login_required
def edit_class(request, class_name):
    context = {

    }
    # waiting class_info
    return render(request, "a_school_admin/edit-class.html", context)


@login_required
def class_detial(request, class_name): 
    context = {

    }
    #, waiting class_info
    return render(request, "a_school_admin/class-detail.html", context)


@login_required
def add_class(request):
    home_room_teachers = [
    {'room_teacher': 'Mr. Smith'},
    {'room_teacher': 'Ms. Johnson'},
    {'room_teacher': 'Dr. Lee'},
    {'room_teacher': 'Mrs. Carter'},
    ]

    classes = [
        {'name': 'Physics', 'code': 'PHY101'},
        {'name': 'Mathematics', 'code': 'MTH102'},
        {'name': 'History', 'code': 'HIS103'},
    ]
    students = [
    ({'username': 'amare'}, {'age': 18}),
    ({'username': 'miki'}, {'age': 19}),
]

    context = {
        'students': students,
        'home_room_teachers': home_room_teachers,
        'classes': classes,
        'school_name': 'Example High School'
    }
    return render(request, "a_school_admin/add-class.html", context)


# ===========================   Teachers View =====================



@login_required
def teachers_mang(request):
    context = {
    }
    # waiting subjects and teachers
    return render(request, "a_school_admin/teachers-mang.html", context)

@login_required
def add_teacher(request):
    return render(request, "a_school_admin/add-teacher.html")


@login_required
def edit_teacher(request, teacher_username):
    return render(request, "a_school_admin/edit-teacher.html")

def teacher_detail(request, teacher_username):
    print("\n\n\n\n", teacher_username)
    return render(request, "a_school_admin/teacher-detail.html")











@login_required
def materials(request):
    pass














student_excel = {}
teacher_excel = {}




def generate_password(length=8, include_uppercase=True, include_digits=True, include_special_chars=True):
    lowercase_letters = string.ascii_lowercase
    uppercase_letters = string.ascii_uppercase if include_uppercase else ''
    digits = string.digits if include_digits else ''
    special_chars = string.punctuation if include_special_chars else ''
    all_chars = lowercase_letters + uppercase_letters + digits + special_chars
    password = ''.join(secrets.choice(all_chars) for _ in range(length))
    return password

def validate_email(email):
    # Regular expression for validating an email
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    
    if not re.match(email_regex, email):
        return False
    return True


def add_students(request):
    if request.method == "POST" and request.FILES.get("file"):
        excel_file = pd.read_excel(request.FILES["file"])
        headers = excel_file.columns

        # Validate headers
        required_columns = ['first name', 'last name', 'middle name', 'email', 'age', 'phone number', 'gender', 'class']
        for column in required_columns:
            if column not in headers:
                messages.error(request, f"'{column}' column is missing in the uploaded file.")
                return render(request, "a_school_admin/upload.html")

        # Loop through each row of the DataFrame
        for idx, row in excel_file.iterrows():
            # Handle missing or NaN values
            if row.isnull().any():
                messages.error(request, f"Missing values in row {idx + 2}. Please ensure all fields are filled.")
                return render(request, "a_school_admin/upload.html")

            class_name = str(row['class']).replace(" ", "")
            grade = ''.join([char for char in class_name if char.isdigit()])
            section = ''.join([char for char in class_name if char.isalpha()])
            
            # Class Validation
            if not grade.isdigit() or int(grade) not in [9, 10, 11, 12]:
                messages.error(request, f"Invalid grade at line {idx + 2}: '{grade}'\n Grade should be a number from 9 to 12.")
                return render(request, "a_school_admin/upload.html")

            if section.upper() not in "ABCDEFGH":
                messages.error(request, f"Invalid section at line {idx + 2}: '{section}'\n Section should be from A to H")
                return render(request, "a_school_admin/upload.html")
            
            if not ClassRoom.objects.filter(class_name=class_name).exists():
                messages.error(request, f"Invalid class name at line {idx + 2}\n '{class_name}' has not been yet registered.")
                return render(request, "a_school_admin/upload.html")

            # Age Validation
            age = row['age']
            if not isinstance(age, (int, float)) or age < 4 or age > 80:
                messages.error(request, f"Invalid age at line {idx + 2}: '{age}'\n Age should be between 4 and 80")
                return render(request, "a_school_admin/upload.html")

            # Phone Number Validation
            phone_number = str(row['phone number'])
            if not phone_number.isdigit() or len(phone_number) != 10:
                messages.error(request, f"Invalid phone number at line {idx + 2}: '{phone_number}'\n Phone number should be 10 digits")
                return render(request, "a_school_admin/upload.html")

            # Gender Validation
            gender = str(row['gender']).upper()
            if gender not in ["M", "F"]:
                messages.error(request, f"Invalid gender at line {idx + 2}: '{gender}'\n Gender should be 'M' or 'F'")
                return render(request, "a_school_admin/upload.html")

            # Name Validation (First, Middle, Last Names)
            first_name = str(row['first name'])
            middle_name = str(row['middle name'])
            last_name = str(row['last name'])


            for name in [first_name, middle_name, last_name]:
                if not name.isalpha():
                    messages.error(request, f"Invalid name at line {idx + 2}: '{name}'\n Name should only contain letters")
                    return render(request, "a_school_admin/upload.html")
                
            # Eamil Validation
            email = str(row['email'])
            if not validate_email(email):
                messages.error(request ,f"Invalid email at line {idx + 2}")
                return render(request, "a_school_admin/upload.html")


        # Save students to the database
        for idx, row in excel_file.iterrows():
            password = generate_password()
            gender = "male" if row["gender"].upper() == "M" else "female"
            try:
                # Create user
                user = CustomUser.objects.create(
                    first_name=row['first name'],
                    middle_name=row['middle name'],
                    last_name=row['last name'],
                    email=row['email'],
                    gender="male" if row["gender"].upper() == "M" else "female",
                    phone_number=row["phone number"],
                    role="student"
                )

                user.set_password(password)
                user.save()


                # Create student
                UserProfile.objects.create(
                    user=user,
                    user_pic=row["pic"],
                    password=password
                )
                
            except Exception as e:
                messages.error(request, f"Error saving student: {str(e)}")
                return render(request, "a_school_admin/upload.html")

        messages.success(request, "Students added successfully.")
        return redirect("admin_dashboard_url")

    return render(request, "a_school_admin/upload.html")

def download_student_excel(request):
    students = CustomUser.objects.filter(role="student")
    student_data = []
    for student in students:
        student_data.append({
            'first_name': student.first_name,
            'middle_name': student.middle_name,
            'last_name': student.last_name,
            'age': student.age,
            'class': ClassRoom.objects.get(student=student).class_name,
            'email': student.email,
        })
    
    # Create DataFrame and save as Excel
    df = pd.DataFrame(student_data)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="students.xlsx"'

    return response
