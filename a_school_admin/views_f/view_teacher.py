from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import check_password
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
    try:
        teachers = CustomUser.objects.filter(role="teacher")
    except Exception:
        messages.warning(request, "No teacher found in the system. Add teachers above.")
        teachers = None

    context = {
        "teachers": teachers, 
    }
    # waiting subjects and teachers
    return render(request, "a_school_admin/teachers-mang.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_teacher(request, teacher_username):
    Teacher = get_user_model()
    teacher = get_object_or_404(Teacher, username=teacher_username)
    teacher_profile = get_object_or_404(UserProfile, user=teacher)
    available_class_rooms = Class.objects.exclude(class_name__in=ClassRoom.objects.values("class_name"))

    context = {
        "teacher_profile": teacher_profile,
        "available_class_rooms": available_class_rooms,
        "home_room_class": ClassRoom.objects.filter(room_teacher=teacher).first().class_name if ClassRoom.objects.filter(room_teacher=teacher).exists() else "",
    }

    if request.method == 'POST':
        try:
            first_name = request.POST.get('first_name', '').strip()
            middle_name = request.POST.get('middle_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            age = request.POST.get('age', '').strip()
            email = request.POST.get('email', '').strip()
            home_room_class = request.POST.get('home_room_class', '').strip()
            password = request.POST.get('password', '').strip()
            profile_image = request.FILES.get('profile_image')

            has_changes = False
            changes = []

            if not Class.objects.filter(class_name=home_room_class).exists():
                messages.error(request, f"'{home_room_class}' doesn't exist.")
                return render(request, "a_school_admin/edit-teachers.html", context)

            current_classroom = ClassRoom.objects.filter(room_teacher=teacher).first()
            new_class = Class.objects.get(class_name=home_room_class)

            if not current_classroom or current_classroom.class_name != new_class:
                if ClassRoom.objects.filter(class_name=new_class).exists():
                    messages.error(request, f"There is already a home room teacher for '{home_room_class}'.")
                    return render(request, "a_school_admin/edit-teachers.html", context)
                if current_classroom:
                    current_classroom.delete()
                ClassRoom.objects.create(class_name=new_class, room_teacher=teacher)
                changes.append("home room class")
                has_changes = True

            if email and email != teacher.email:
                if not validate_email(email):
                    messages.error(request, "Invalid Email Format!")
                    return render(request, "a_school_admin/edit-teachers.html", context)
                if CustomUser.objects.filter(email=email).exclude(pk=teacher.pk).exists():
                    messages.error(request, "Email already exists.")
                    return render(request, "a_school_admin/edit-teachers.html", context)
                teacher.email = email
                changes.append("email")
                has_changes = True

            if first_name and first_name != teacher.first_name:
                teacher.first_name = first_name
                changes.append("first name")
                has_changes = True

            if middle_name != teacher.middle_name:
                teacher.middle_name = middle_name
                changes.append("middle name")
                has_changes = True

            if last_name and last_name != teacher.last_name:
                teacher.last_name = last_name
                changes.append("last name")
                has_changes = True

            if phone_number and re.match(r'^\+?[0-9]{8,15}$', phone_number) and phone_number != teacher.phone_number:
                teacher.phone_number = phone_number
                changes.append("phone number")
                has_changes = True
            elif not re.match(r'^\+?[0-9]{8,15}$', phone_number):
                messages.error(request, "Invalid phone number format. Use +1234567890 format.")
                return render(request, "a_school_admin/edit-teachers.html", context)

            try:
                age = int(age)
                if not (1 <= age <= 120):
                    messages.error(request, "Age must be between 1 and 120.")
                    return render(request, "a_school_admin/edit-teachers.html", context)
                if age != teacher.age:
                    teacher.age = age
                    changes.append("age")
                    has_changes = True
            except ValueError:
                messages.error(request, "Age must be a valid number.")
                return render(request, "a_school_admin/edit-teachers.html", context)

            if password and not check_password(password, teacher.password):
                teacher.set_password(password)
                changes.append("password")
                has_changes = True

            if profile_image and profile_image != teacher_profile.user_pic:
                teacher_profile.user_pic = profile_image
                changes.append("profile image")
                has_changes = True

            if has_changes:
                teacher.save()
                teacher_profile.save()
                AdminAction.objects.create(
                    admin=request.user,
                    action=f"Edited User ({teacher.username}): Updated {', '.join(changes)}"
                )
                messages.success(request, 'Teacher updated successfully.')
            else:
                messages.info(request, 'No changes detected.')

            return redirect('teachers_mang_url')

        except Exception as e:
            messages.error(request, f"Update failed: {str(e)}")

    return render(request, "a_school_admin/edit-teachers.html", context)


def teacher_detail(request, teacher_username):
    try:
        teacher_user = CustomUser.objects.get(username=teacher_username)
        teacher = get_object_or_404(UserProfile, user=teacher_user)
    except UserProfile.DoesNotExist:
        messages.error(request, "UserProfile not found for the given username.")
        return redirect("teachers_mang_url")

    context = {
        "teacher": teacher,
        "home_room": ClassRoom.objects.get(room_teacher=teacher.user).class_name,
    }
    return render(request, "a_school_admin/teacher-detail.html", context)

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_teacher(request):
    teachers_not_in_classroom = UserProfile.objects.filter(
        user__role='teacher'
    ).exclude(
        user__id__in=ClassRoom.objects.values_list("room_teacher", flat=True)
    )
    available_class_rooms = Class.objects.exclude(class_name__in=ClassRoom.objects.values("class_name"))
    context = {
        "class_list": Class.objects.values_list("class_name", flat=True).order_by(Length('class_name'), 'class_name'),
        "available_class_rooms": available_class_rooms,
    }

    if request.method == 'POST':
        try:
            first_name = request.POST.get("first_name", "").strip()
            middle_name = request.POST.get("middle_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            age = request.POST.get("age", "").strip()
            gender = request.POST.get("gender", "").strip()
            email = request.POST.get('email', "").strip()
            profile_pic = request.FILES.get("profile_pic")
            home_room_class = request.POST.get('home_room_class')
            password = request.POST.get('password', "").strip()
            conf_password = request.POST.get('confirm_password', "").strip()

            # Check if class exists and no home room teacher is already assigned
            if ClassRoom.objects.filter(class_name__class_name=home_room_class).exists():
                messages.warning(request, f"There is already a home room teacher for {home_room_class}.")
                return render(request, "a_school_admin/add-teacher.html", context)
            elif not Class.objects.filter(class_name=home_room_class).exists():
                messages.error(request, f"'{home_room_class}' Doesn't exist.")
                return render(request, "a_school_admin/add-teacher.html", context)

            # Validate email
            if not email:
                messages.error(request, "Email is required!")
                return render(request, "a_school_admin/add-teacher.html", context)
            
            if not validate_email(email):
                messages.error(request, "Invalid email format!")
                return render(request, "a_school_admin/add-teacher.html", context)
            
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return render(request, "a_school_admin/add-teacher.html", context)

            # Validate other fields
            if not first_name:
                messages.error(request, "First name is required!")
                return render(request, "a_school_admin/add-teacher.html", context)
            
            if not last_name:
                messages.error(request, "Last name is required!")
                return render(request, "a_school_admin/add-teacher.html", context)

            if not phone_number:
                messages.error(request, "Phone number is required!")
                return render(request, "a_school_admin/add-teacher.html", context)
            
            if not re.match(r'^\+?[0-9]{8,15}$', phone_number):
                messages.error(request, "Invalid phone number format. Use +1234567890 format.")
                return render(request, "a_school_admin/add-teacher.html", context)

            if not age:
                messages.error(request, "Age is required!")
                return render(request, "a_school_admin/add-teacher.html", context)
            
            try:
                age = int(age)
                if age < 18 or age > 90:
                    messages.error(request, "Age must be between 18 and 90.")
                    return render(request, "a_school_admin/add-teacher.html", context)
            except ValueError:
                messages.error(request, "Age must be a valid number.")
                return render(request, "a_school_admin/add-teacher.html", context)

            if not gender:
                messages.error(request, "Gender is required!")
                return render(request, "a_school_admin/add-teacher.html", context)
            elif gender.upper() not in ["MALE", "FEMALE"]:
                messages.error(request, "Invalid gender value")
                return render(request, "a_school_admin/add-teacher.html", context)

            if not password:
                messages.error(request, "Password cannot be empty!")
                return render(request, "a_school_admin/add-teacher.html", context)

            if not password == conf_password:
                messages.error(request, f"Passwords doesn't match.")
                return render(request, "a_school_admin/add-teacher.html", context)

            # Create teacher
            teacher = CustomUser(
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                phone_number=phone_number,
                age=age,
                role="teacher",
                gender=gender,
                email=email,
            )
            teacher.set_password(password)
            teacher.save()

            # Create ClassRoom object
            try:
                class_obj = Class.objects.get(class_name=home_room_class)
                classroom = ClassRoom(
                    class_name=class_obj,
                    room_teacher=teacher,
                )
                classroom.save()

                # Save profile picture if provided

                if profile_pic:
                    teacher_profile = UserProfile(
                        user=teacher,
                        user_pic=profile_pic,
                    )
                    teacher_profile.save()
                else:
                    messages.error("Profile picture faile to load.")
                    return redirect('teachers_mang_url')
                

                # Log admin action
                admin_action = AdminAction(
                    admin=request.user,
                    action=f"Added User ({teacher.first_name})"
                )
                admin_action.save()

                messages.success(request, 'Teacher added successfully.')
                return redirect('teachers_mang_url')  # Ensure this URL exists in your urls.py

            except Class.DoesNotExist:
                messages.error(request, f"Class {home_room_class} does not exist.")
                return render(request, "a_school_admin/add-teacher.html", context)

        except Exception as e:
            messages.error(request, f"Failed to add teacher: {str(e)}")
            return render(request, "a_school_admin/add-teacher.html", context)

    return render(request, "a_school_admin/add-teacher.html", context)

@user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
def add_teachers(request):
    REQUIRED_COLUMNS = ['first name', 'last name', 'middle name', 'email', 'age', 'phone number', 'gender', 'home room class']
    CLASS_REGEX = r'^\d{1,2}[A-H]$'

    context = {
        'upload_for': "Teachers",
        'upload_title': 'Upload Teachers',
        'required_columns': REQUIRED_COLUMNS,
        'errors': [],
        'recommendations': [],
    }

    if request.method == "POST":
        file = request.FILES.get("file")
        if not file or not file.name.endswith(('.xls', '.xlsx')):
            context['errors'].append("Please upload a valid Excel file.")
            return render(request, "a_school_admin/upload.html", context)

        try:
            df = pd.read_excel(file, dtype={'phone number': str, 'home room class': str}).fillna('')
        except Exception as e:
            context['errors'].append(f"Error reading file: {e}")
            return render(request, "a_school_admin/upload.html", context)

        cols = [col.lower() for col in df.columns]
        missing = [col for col in REQUIRED_COLUMNS if col.lower() not in cols]
        if missing:
            context['errors'].append(f"Missing columns: {', '.join(missing)}")
            return render(request, "a_school_admin/upload.html", context)

        existing_classes = set(Class.objects.values_list("class_name", flat=True))
        taken_home_rooms = set(ClassRoom.objects.values_list("class_name__class_name", flat=True))
        existing_emails = set(CustomUser.objects.values_list("email", flat=True))

        errors, to_create = [], []
        for idx, row in df.iterrows():
            line = idx + 2
            row_data = {col: str(row[col]).strip() for col in REQUIRED_COLUMNS}
            row_errors = []

            if any(not v for v in row_data.values()):
                row_errors.append(f"Line {line}: Missing required fields.")

            # Validate class
            home_class = row_data['home room class'].upper()
            if home_class and not re.match(CLASS_REGEX, home_class):
                row_errors.append(f"Line {line}: Invalid class format '{home_class}'")
            elif home_class not in existing_classes:
                context['recommendations'] = sorted(existing_classes)
                row_errors.append(f"Line {line}: Class '{home_class}' not found")
            elif home_class in taken_home_rooms:
                row_errors.append(f"Line {line}: Class '{home_class}' already assigned")

            # Validate age
            try:
                age = int(row_data['age'])
                if not 4 <= age <= 80:
                    row_errors.append(f"Line {line}: Invalid age {age}")
            except:
                row_errors.append(f"Line {line}: Age must be a number")

            # Validate phone
            phone = row_data['phone number']
            if not (phone.isdigit() and len(phone) == 10):
                row_errors.append(f"Line {line}: Invalid phone number '{phone}'")

            # Gender
            gender = row_data['gender'].upper()
            if gender not in ['M', 'F']:
                row_errors.append(f"Line {line}: Invalid gender '{gender}'")

            # Names
            for n in ['first name', 'middle name', 'last name']:
                if not re.match(r'^[A-Za-z\- ]+$', row_data[n]):
                    row_errors.append(f"Line {line}: Invalid {n} '{row_data[n]}'")

            # Email
            email = row_data['email'].lower()
            if not validate_email(email):
                row_errors.append(f"Line {line}: Invalid email format")
            elif email in existing_emails:
                row_errors.append(f"Line {line}: Email already exists")

            if row_errors:
                errors.extend(row_errors)
            else:
                to_create.append((row_data, home_class, age, gender, email))

        if errors:
            context['errors'] = errors
            return render(request, "a_school_admin/upload.html", context)

        try:
            with transaction.atomic():
                new_users = []
                for row_data, home_class, age, gender, email in to_create:
                    pwd = generate_password()
                    user = CustomUser.objects.create(
                        first_name=row_data['first name'],
                        middle_name=row_data['middle name'],
                        last_name=row_data['last name'],
                        email=email,
                        age=age,
                        gender='male' if gender == 'M' else 'female',
                        phone_number=row_data['phone number'],
                        role="teacher"
                    )
                    user.set_password(pwd)
                    user.save()

                    class_obj = Class.objects.get(class_name=home_class)
                    ClassRoom.objects.create(class_name=class_obj, room_teacher=user)
                    UserProfile.objects.create(user=user, password=pwd)
                    new_users.append(user)

                AdminAction.objects.create(
                    admin=request.user,
                    action=f"Bulk added {len(new_users)} teachers"
                )
                messages.success(request, f"Successfully added {len(new_users)} teachers")
                return redirect('teachers_mang_url')

        except Exception as e:
            context['errors'].append(f"System error: {str(e)}")

    return render(request, "a_school_admin/upload.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def download_teacher_excel_template(request):
    columns = ['first name', 'last name', 'middle name', 'email',
               'age', 'phone number', 'gender', 'home room class', 'class']

    # Optional: Add an empty DataFrame with the right columns
    df = pd.DataFrame(columns=columns)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="teacher_template.xlsx"'

    df.to_excel(response, index=False)
    return response

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