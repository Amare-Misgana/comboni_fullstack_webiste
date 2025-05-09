from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
from a_school_admin.models import AdminAction
import pandas as pd
from common.models import UserProfile, CustomUser, ClassRoom, Class
import re
from django.db.models.functions import Length
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
    context = {
        'upload_for': "Teachers",
        'upload_title': 'Upload Teachers',
        'required_columns': ['first name', 'last name', 'middle name', 'email', 
                           'age', 'phone number', 'gender', 'home room class'],
        'errors': [],
        'recommendations': [],
    }

    if request.method == "POST":
        
        if 'file' not in request.FILES or not request.FILES['file'].name.endswith(('.xls', '.xlsx')):
            context['errors'].append("Please upload a valid Excel file.")
            return render(request, "a_school_admin/upload.html", context)

        try:
            
            df = pd.read_excel(
                request.FILES["file"],
                dtype={'phone number': str, 'home room class': str}
            ).fillna('')  
        except Exception as e:
            context['errors'].append(f"Error reading file: {str(e)}")
            return render(request, "a_school_admin/upload.html", context)

        
        missing_columns = [col for col in context['required_columns'] 
                         if col.lower() not in map(str.lower, df.columns)]
        if missing_columns:
            context['errors'].append(f"Missing columns: {', '.join(missing_columns)}")
            return render(request, "a_school_admin/upload.html", context)

        
        validation_errors = []
        show_recommendations = False

        for idx, row in df.iterrows():
            row_errors = []
            line_num = idx + 2 
            
            
            empty_fields = [col for col in context['required_columns'] 
                          if not str(row[col]).strip()]
            if empty_fields:
                row_errors.append(f"Line {line_num}: Missing values for {', '.join(empty_fields)}")

            
            class_name = str(row['class']).strip().upper()
            if not re.match(r'^\d{1,2}[A-H]$', class_name):
                row_errors.append(f"Line {line_num}: Invalid class format '{class_name}' (expected format like '11A')")
            if not Class.objects.filter(class_name=class_name).exists():
                show_recommendations = True
                row_errors.append(f"Line {line_num}: Class '{class_name}' not found in system")

            home_room_class = str(row["home room class"]).strip().upper()
            if home_room_class:
                print("checking.....")
                # 1) format
                if not re.match(r'^\d{1,2}[A-H]$', home_room_class):
                    row_errors.append(
                        f"Line {line_num}: Invalid class format '{home_room_class}' (expected like '11A')"
                    )
                # 2) existence
                if not Class.objects.filter(class_name=home_room_class).exists():
                    show_recommendations = True
                    row_errors.append(
                        f"Line {line_num}: Class '{home_room_class}' not found in system"
                    )
                # 3) already assigned
                if ClassRoom.objects.filter(class_name__class_name=home_room_class).exists():
                    row_errors.append(
                        f"Line {line_num}: Home-room position already taken for '{home_room_class}'"
                    )
            else:
                print("checked!!!!!")
                home_room_class = None 

            
            try:
                age = int(row['age'])
                if not 4 <= age <= 80:
                    row_errors.append(f"Line {line_num}: Invalid age {age} (4-80 only)")
            except (ValueError, TypeError):
                row_errors.append(f"Line {line_num}: Invalid age format")

            
            phone = str(row['phone number']).strip()
            if len(phone) != 10 or not phone.isdigit():
                row_errors.append(f"Line {line_num}: Invalid phone number '{phone}' (10 digits required)")

            
            gender = str(row['gender']).upper()
            if gender not in ['M', 'F']:
                row_errors.append(f"Line {line_num}: Invalid gender '{gender}' (M/F only)")

            
            for field in ['first name', 'middle name', 'last name']:
                name = str(row[field]).strip()
                if not re.match(r'^[A-Za-z\- ]+$', name):
                    row_errors.append(f"Line {line_num}: Invalid {field} '{name}' (letters and hyphens only)")

            
            email = str(row['email']).strip().lower()
            if not validate_email(email):
                row_errors.append(f"Line {line_num}: Invalid email format")
            elif CustomUser.objects.filter(email=email).exists():
                row_errors.append(f"Line {line_num}: Email already exists")

            if row_errors:
                validation_errors.extend(row_errors)
        if show_recommendations:
            context['recommendations'].extend(
                Class.objects.values_list("class_name", flat=True).order_by(Length('class_name'), 'class_name')
            )

    
        if validation_errors:
            context['errors'] = validation_errors
            return render(request, "a_school_admin/upload.html", context)

        
        try:
            with transaction.atomic():
                created_users = []
                for _, row in df.iterrows():
                    password = generate_password()
                    class_name = str(row['home room class']).strip().upper()
                    
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

                    class_name_ = Class.objects.get(class_name=row['class'])
                    ClassRoom.objects.create(
                        class_name=class_name_,
                        room_teacher=user,
                    )
                    
                    
                    if hasattr(user, 'classroom'):
                        classroom = Class.objects.get(class_name=class_name)
                        user.classroom = classroom
                        user.save()
                    
                    
                    UserProfile.objects.create(
                        user=user,
                        password=password,
                    )
                    created_users.append(user)

                
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