from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
from a_school_admin.models import AdminAction
import pandas as pd
from common.models import UserProfile, CustomUser, ClassRoom, Class
import re
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

# @user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
# def add_teachers(request):
#     if request.method == "POST" and request.FILES.get("file"):
#         excel_file = pd.read_excel(request.FILES["file"])
#         headers = excel_file.columns
#         required_columns = ['first name', 'last name', 'middle name', 'email', 'age', 'phone number', 'gender', 'home room']

#         for column in required_columns:
#             if column not in headers:
#                 messages.error(request, f"'{column}' column is missing in the uploaded file.")
#                 return render(request, "a_school_admin/upload.html")

#         for idx, row in excel_file.iterrows():
#             if row.isnull().any():
#                 messages.error(request, f"Missing values in row {idx + 2}.")
#                 return render(request, "a_school_admin/upload.html")

#             class_name = str(row['class']).replace(" ", "")
#             grade = ''.join(filter(str.isdigit, class_name))
#             section = ''.join(filter(str.isalpha, class_name))

#             if not grade.isdigit() or int(grade) not in [9, 10, 11, 12]:
#                 messages.error(request, f"Invalid grade at line {idx + 2}: '{grade}'")
#                 return render(request, "a_school_admin/upload.html")

#             if section.upper() not in "ABCDEFGH":
#                 messages.error(request, f"Invalid section at line {idx + 2}: '{section}'")
#                 return render(request, "a_school_admin/upload.html")

#             if not ClassRoom.objects.filter(class_name=class_name).exists():
#                 messages.error(request, f"Invalid class name at line {idx + 2}: '{class_name}'")
#                 return render(request, "a_school_admin/upload.html")

#             age = row['age']
#             if not isinstance(age, (int, float)) or age < 4 or age > 80:
#                 messages.error(request, f"Invalid age at line {idx + 2}: '{age}'")
#                 return render(request, "a_school_admin/upload.html")

#             phone_number = str(row['phone number'])
#             if not phone_number.isdigit() or len(phone_number) != 10:
#                 messages.error(request, f"Invalid phone number at line {idx + 2}: '{phone_number}'")
#                 return render(request, "a_school_admin/upload.html")

#             gender = str(row['gender']).upper()
#             if gender not in ["M", "F"]:
#                 messages.error(request, f"Invalid gender at line {idx + 2}: '{gender}'")
#                 return render(request, "a_school_admin/upload.html")

#             for name in [row['first name'], row['middle name'], row['last name']]:
#                 if not str(name).isalpha():
#                     messages.error(request, f"Invalid name at line {idx + 2}: '{name}'")
#                     return render(request, "a_school_admin/upload.html")

#             email = str(row['email'])
#             if not validate_email(email):
#                 messages.error(request, f"Invalid email at line {idx + 2}")
#                 return render(request, "a_school_admin/upload.html")

#         for idx, row in excel_file.iterrows():
#             password = generate_password()
#             try:
#                 user = CustomUser.objects.create(
#                     first_name=row['first name'],
#                     middle_name=row['middle name'],
#                     last_name=row['last name'],
#                     email=row['email'],
#                     gender="male" if row["gender"].upper() == "M" else "female",
#                     phone_number=row["phone number"],
#                     role="teacher"
#                 )
#                 user.set_password(password)
#                 user.save()

#                 UserProfile.objects.create(
#                     user=user,
#                     user_pic=row.get("pic", ""),
#                     password=password
#                 )
#             except Exception as e:
#                 messages.error(request, f"Error saving teacher: {str(e)}")
#                 return render(request, "a_school_admin/upload.html")

#         messages.success(request, "Teachers added successfully.")
#         return redirect("admin_dashboard_url")

#     return render(request, "a_school_admin/upload.html")


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_teachers(request):
    context = {
        'upload_for': "Teachers",
        'upload_title': 'Upload Teachers',
        'required_columns': ['first name', 'last name', 'middle name', 'email', 
                           'age', 'phone number', 'gender', 'home room class'],
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
                        role="teacher"
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
                    action=f"Bulk added {len(created_users)} teachers"
                )

                messages.success(request, f"Successfully added {len(created_users)} teachers")
                return redirect('teachers_mang_url')

        except Exception as e:
            context['errors'].append(f"System error: {str(e)}")
            return render(request, "a_school_admin/upload.html", context)

    return render(request, "a_school_admin/upload.html", context)

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def download_teacher_excel(request):
    teachers = CustomUser.objects.filter(role="teacher")
    teacher_data = []
    for teacher in teachers:
        if ClassRoom.objects.filter(room_teacher=teacher).exists():
            room_class = ClassRoom.objects.get(room_teacher=teacher).class_name
        else:
            room_class = "Not Set"
        try:
            teacher_data.append({
                'first_name': teacher.first_name,
                'middle_name': teacher.middle_name,
                'last_name': teacher.last_name,
                'phone_number': teacher.phone_number,
                'age': teacher.age,
                'room class': room_class,
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