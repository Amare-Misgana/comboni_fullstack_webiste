from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
from a_school_admin.models import AdminAction
import pandas as pd
from common.models import UserProfile, CustomUser, ClassRoom, Class
import openpyxl
from io import BytesIO
import re
import numpy as np


#    helper function
from a_school_admin.helper_func import generate_password, validate_email

#    Global Variables
student_excel = {}


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def students_mang(request):
    User = get_user_model()
    students = User.objects.filter(role='student')
    context = {
        "students": students,
    }
    return render(request, "a_school_admin/students-mang.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def delete_student(request, student_username):
    student = CustomUser.objects.get(username=student_username)
    try:
        student_name = UserProfile.objects.get(user=student)
        student.delete()
        messages.success(request, f"Deleting {student_name.username} successfully.")
    except Exception as e:
        messages.error(request, f"Deletion faild: {e}")

    return render(request, "a_school_admin/students-mang.html", context)



@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_student(request, student_username):
    Student = get_user_model()
    student = Student.objects.get(username=student_username)
    student_profile = get_object_or_404(UserProfile, user=student)
    context = {"student_profile": student_profile}

    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.POST.get('first_name', '').strip()
            middle_name = request.POST.get('middle_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            age = request.POST.get('age', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '').strip()
            profile_image = request.FILES.get('profile_image')

            # Track changes
            has_changes = False
            changes = []

            # Email validation
            if email != student.email:
                if not validate_email(email):
                    messages.error(request, "Invalid Email Format!")
                    return render(request, "a_school_admin/edit-students.html", context)
                if CustomUser.objects.filter(email=email).exclude(email=student.email).exists():
                    messages.error(request, "Email already exists.")
                    return render(request, "a_school_admin/edit-students.html", context)
                student.email = email
                changes.append("email")
                has_changes = True

            # Name validations
            if not first_name:
                messages.error(request, "First name is required.")
                return render(request, "a_school_admin/edit-students.html", context)
            if first_name != student.first_name:
                student.first_name = first_name
                changes.append("first name")
                has_changes = True

            if middle_name != student.middle_name:
                student.middle_name = middle_name
                changes.append("middle name")
                has_changes = True

            if not last_name:
                messages.error(request, "Last name is required.")
                return render(request, "a_school_admin/edit-students.html", context)
            if last_name != student.last_name:
                student.last_name = last_name
                changes.append("last name")
                has_changes = True

            # Phone validation
            if not re.match(r'^\+?[0-9]{8,15}$', phone_number):
                messages.error(request, "Invalid phone number format. Use +1234567890 format.")
                return render(request, "a_school_admin/edit-students.html", context)
            if phone_number != student.phone_number:
                student.phone_number = phone_number
                changes.append("phone number")
                has_changes = True

            # Age validation
            try:
                age = int(age)
                if not (1 <= age <= 120):
                    messages.error(request, "Age must be between 1 and 120.")
                    return render(request, "a_school_admin/edit-students.html", context)
                if age != student.age:
                    student.age = age
                    changes.append("age")
                    has_changes = True
            except ValueError:
                messages.error(request, "Age must be a valid number.")
                return render(request, "a_school_admin/edit-students.html", context)

            # Password update (only if provided)
            if password and student_profile.password != password:
                student.set_password(password)
                student_profile.password = password
                changes.append("password")
                has_changes = True

            # Profile image update (only if provided)
            if profile_image and profile_image != student_profile:
                student_profile.user_pic = profile_image
                changes.append("profile image")
                has_changes = True

            # Save only if changes exist
            if has_changes:
                student.save()
                student_profile.save()
                AdminAction.objects.create(
                    admin=request.user,
                    action=f"Edited User ({student.first_name}): Updated {', '.join(changes)}"
                )
                messages.success(request, 'Student updated successfully.')
            else:
                messages.info(request, 'No changes detected.')

            return redirect('students_mang_url')

        except Exception as e:
            messages.error(request, f"Update failed: {str(e)}")
            return render(request, "a_school_admin/edit-students.html", context)

    return render(request, "a_school_admin/edit-students.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_student(request):
    context = {
        "class_list": Class.objects.values_list("class_name", flat=True)
    }

    if request.method == 'POST':
        try:
            first_name = request.POST.get("first_name", "").strip()
            middle_name = request.POST.get("middle_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            age = request.POST.get("age", "").strip()
            gender = request.POST.get("gender", "").strip()
            password = request.POST.get('password', "").strip()
            email = request.POST.get('email', "").strip()
            profile_pic = request.FILES.get("profile_pic")
            class_name = request.POST.get("class_name")

            if not class_name:
                messages.error(request, "Class is required!")
                return render(request, "a_school_admin/add-student.html", context)

            if not email:
                messages.error(request, "Email is required!")
                return render(request, "a_school_admin/add-student.html", context)
            
            if not validate_email(email):
                messages.error(request, "Invalid email format!")
                return render(request, "a_school_admin/add-student.html", context)
            
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return render(request, "a_school_admin/add-student.html", context)

            if not first_name:
                messages.error(request, "First name is required!")
                return render(request, "a_school_admin/add-student.html", context)
            
            if not last_name:
                messages.error(request, "Last name is required!")
                return render(request, "a_school_admin/add-student.html", context)

            if not phone_number:
                messages.error(request, "Phone number is required!")
                return render(request, "a_school_admin/add-student.html", context)
            
            if not re.match(r'^\+?[0-9]{8,15}$', phone_number):
                messages.error(request, "Invalid phone number format. Use +1234567890 format.")
                return render(request, "a_school_admin/add-student.html", context)

            if not age:
                messages.error(request, "Age is required!")
                return render(request, "a_school_admin/add-student.html", context)
            
            try:
                age = int(age)
                if age < 5 or age > 90:
                    messages.error(request, "Age must be between 5 and 90.")
                    return render(request, "a_school_admin/add-student.html", context)
            except ValueError:
                messages.error(request, "Age must be a valid number.")
                return render(request, "a_school_admin/add-student.html", context)

            if not gender:
                messages.error(request, "Gender is required!")
                return render(request, "a_school_admin/add-student.html", context)
            

            if not password:
                messages.error(request, "Password cannot be empty!")
                return render(request, "a_school_admin/add-student.html", context)

            student = CustomUser(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                phone_number=phone_number,
                age=age,
                role="student",
                gender=gender,
                email=email,
            )
            student.set_password(password)
            student.save()

            ClassRoom(
                class_name=class_name,
                student=student,
            )

            # Save profile picture if provided
            if profile_pic:
                student_profile = UserProfile(
                    user=student,
                    user_pic=profile_pic,
                )
                student_profile.save()

            # Log admin action
            admin_action = AdminAction(
                admin=request.user,
                action=f"Added User ({student.first_name})"
            )
            admin_action.save()

            messages.success(request, 'Student added successfully.')
            return redirect('students_mang_url')

        except Exception as e:
            messages.error(request, f"Failed to add student: {str(e)}")
            return render(request, "a_school_admin/add-student.html", context)

    return render(request, "a_school_admin/add-student.html", context)

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
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




@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_students(request):
    context = {
        'required_columns': ['first name', 'last name', 'middle name', 'email', 
                           'age', 'phone number', 'gender', 'class'],
        'errors': []
    }

    if request.method == "POST":
        # File validation
        if 'file' not in request.FILES or not request.FILES['file'].name.endswith(('.xls', '.xlsx')):
            context['errors'].append("Please upload a valid Excel file.")
            return render(request, "a_school_admin/upload.html", context)

        try:
            # Read Excel with proper type handling
            df = pd.read_excel(
                request.FILES["file"],
                dtype={'phone number': str, 'class': str}
            ).fillna('')  # Replace NaN with empty string
        except Exception as e:
            context['errors'].append(f"Error reading file: {str(e)}")
            return render(request, "a_school_admin/upload.html", context)

        # Column validation
        missing_columns = [col for col in context['required_columns'] 
                         if col.lower() not in map(str.lower, df.columns)]
        if missing_columns:
            context['errors'].append(f"Missing columns: {', '.join(missing_columns)}")
            return render(request, "a_school_admin/upload.html", context)

        # Data validation
        validation_errors = []
        for idx, row in df.iterrows():
            row_errors = []
            line_num = idx + 2  # Excel is 1-indexed + header row
            
            # Check for empty values
            empty_fields = [col for col in context['required_columns'] 
                          if not str(row[col]).strip()]
            if empty_fields:
                row_errors.append(f"Line {line_num}: Missing values for {', '.join(empty_fields)}")

            # Class validation
            class_name = str(row['class']).strip().upper()
            if not re.match(r'^\d{1,2}[A-H]$', class_name):
                row_errors.append(f"Line {line_num}: Invalid class format '{class_name}' (expected format like '11A' with section being from A-H)")
            elif not Class.objects.filter(class_name=class_name).exists():
                row_errors.append(f"Line {line_num}: Class '{class_name}' not found in system")

            # Age validation
            try:
                age = int(row['age'])
                if not 4 <= age <= 80:
                    row_errors.append(f"Line {line_num}: Invalid age {age} (4-80 only)")
            except (ValueError, TypeError):
                row_errors.append(f"Line {line_num}: Invalid age format")

            # Phone validation
            phone = str(row['phone number']).strip()
            if len(phone) != 10 or not phone.isdigit():
                row_errors.append(f"Line {line_num}: Invalid phone number '{phone}' (10 digits required)")

            # Gender validation
            gender = str(row['gender']).upper()
            if gender not in ['M', 'F']:
                row_errors.append(f"Line {line_num}: Invalid gender '{gender}' (M/F only)")

            # Name validation (allowing spaces and hyphens)
            for field in ['first name', 'middle name', 'last name']:
                name = str(row[field]).strip()
                if not re.match(r'^[A-Za-z\- ]+$', name):
                    row_errors.append(f"Line {line_num}: Invalid {field} '{name}' (letters and hyphens only)")

            # Email validation
            email = str(row['email']).strip().lower()
            if not validate_email(email):
                row_errors.append(f"Line {line_num}: Invalid email format")
            elif CustomUser.objects.filter(email=email).exists():
                row_errors.append(f"Line {line_num}: Email already exists")

            if row_errors:
                validation_errors.extend(row_errors)

        if validation_errors:
            context['errors'] = validation_errors
            return render(request, "a_school_admin/upload.html", context)

        # Create users in transaction
        try:
            with transaction.atomic():
                created_users = []
                for _, row in df.iterrows():
                    password = generate_password()
                    class_name = str(row['class']).strip().upper()
                    
                    user = CustomUser(
                        first_name=row['first name'].strip(),
                        middle_name=row['middle name'].strip(),
                        last_name=row['last name'].strip(),
                        email=row['email'].strip().lower(),
                        age=int(row['age']),
                        gender='male' if str(row['gender']).upper() == 'M' else 'female',
                        phone_number=str(row['phone number']).strip(),
                        role="student"
                    )
                    user.set_password(password)
                    user.save()
                    
                    # Assign classroom if relationship exists
                    if hasattr(user, 'classroom'):
                        classroom = ClassRoom.objects.get(class_name=class_name)
                        user.classroom = classroom
                        user.save()
                    
                    # Create profile
                    UserProfile.objects.create(user=user)
                    created_users.append(user)

                # Log admin action
                AdminAction.objects.create(
                    admin=request.user,
                    action=f"Bulk added {len(created_users)} students"
                )

                messages.success(request, f"Successfully added {len(created_users)} students")
                return redirect('students_mang_url')

        except Exception as e:
            context['errors'].append(f"System error: {str(e)}")
            return render(request, "a_school_admin/upload.html", context)

    return render(request, "a_school_admin/upload.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def download_students_excel(request):
    students = CustomUser.objects.filter(role="student")
    student_data = []
    for student in students:
        student_data.append({
            'first_name': student.first_name,
            'middle_name': student.middle_name,
            'last_name': student.last_name,
            'gender': student.gender,
            'age': student.age,
            # 'class': ClassRoom.objects.get(student=student).class_name,
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
