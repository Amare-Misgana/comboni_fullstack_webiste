from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.db import transaction
from a_school_admin.models import AdminAction
import pandas as pd
from common.models import UserProfile, CustomUser, ClassRoom, Class, Conduct
from django.db.models.functions import Length
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from io import BytesIO
import re


from a_school_admin.helper_func import generate_password, validate_email


default_avatar_path = "avatars/default-avatar.png"

identify = {
    "is_admin": True,
    "is_teacher": False,
    "is_student": False,
}

student_excel = {}


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def students_mang(request):
    try:
        classrooms = ClassRoom.objects.all()
    except ObjectDoesNotExist:
        messages.warning(request, "No classrooms found")
        classrooms = None

    context = {
        "classrooms": classrooms,
        "students_": CustomUser.objects.filter(role="student"),
    }
    context.update(identify)
    return render(request, "a_school_admin/students-mang.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def delete_student(request, student_username):
    Student = get_user_model()
    if request.method == "POST":
        try:
            student = Student.objects.get(username=student_username)
            student_profile = UserProfile.objects.get(user=student)
            AdminAction.objects.create(
                admin=request.user,
                action=f"Deleted Teacher ({student_profile.username})",
            )
            student.delete()
            messages.success(request, "Student deleted successfully.")
        except Student.DoesNotExist:
            messages.error(request, "Student couldn't be found.")

    return redirect("students_mang_url")


@user_passes_test(
    lambda user: user.is_authenticated
    and user.role == "admin"
    or user.role == "teacher"
)
def student_detail(request, student_username):
    try:
        student = CustomUser.objects.get(username=student_username)
        try:
            student_profile = UserProfile.objects.get(user=student)
            student_class = student_profile.classroom_students.all().first()
            if not student_profile.user_pic:
                messages.warning(
                    request, "Student Profile is incomplete. Add profile picture"
                )
        except UserProfile.DoesNotExist:
            messages.warning(
                request, "Student Profile is incomplete. Compelete Profile"
            )
            return redirect(
                reverse(
                    "edit_student_url", kwargs={"student_username": student_username}
                )
            )
    # conduct = Conduct
    except CustomUser.DoesNotExist:
        messages.error(request, "Student can't be found!")
        return redirect("students_mang_url")
    conduct = Conduct.objects.filter(student__user=student).first()
    if not conduct:
        student_profile = UserProfile.objects.get(user=student)
        conduct = Conduct.objects.create(student=student_profile)
    print(conduct.conduct)
    context = {
        "student": student,
        "student_profile": student_profile,
        "student_class": student_class,
        "conduct": conduct,
        "only_back": True if request.user.role == "teacher" else False,
    }
    context.update(identify)
    return render(request, "a_school_admin/student-detail.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_student(request):
    context = {
        "class_list": Class.objects.values_list("class_name", flat=True).order_by(
            Length("class_name"), "class_name"
        )
    }
    context.update(identify)

    if request.method == "POST":
        try:
            first_name = request.POST.get("first_name", "").strip()
            middle_name = request.POST.get("middle_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            age = request.POST.get("age", "").strip()
            gender = request.POST.get("gender", "").strip()
            password = request.POST.get("password", "").strip()
            email = request.POST.get("email", "").strip()
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

            if not re.match(r"^\+?[0-9]{8,15}$", phone_number):
                messages.error(
                    request, "Invalid phone number format. Use +1234567890 format."
                )
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

            if profile_pic and profile_pic.size > settings.MAX_UPLOAD_SIZE:
                messages.error(request, "Profile picture must be less than 3MB.")
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

            try:
                class_instance = Class.objects.get(class_name=class_name)
            except Class.DoesNotExist:
                messages.error(request, "Class Doesn't Exists.")
                return redirect("student_mang_url")

            try:
                student_profile = UserProfile.objects.create(
                    user=student, user_pic=profile_pic, password=password
                )
            except Exception as e:
                student.delete()
                messages.error(request, f"Failed to create student profile: {e}")
                return redirect("students_mang_url")

            try:
                class_room, created = ClassRoom.objects.get_or_create(
                    class_name=class_instance
                )
                class_room.students.add(student_profile)
            except Exception as e:
                messages.error(request, f"Can't create the class: {e}")
                return redirect("students_mang_url")
            try:
                admin_action = AdminAction(
                    admin=request.user,
                    action=f"Added Student ({student_profile.user.first_name})",
                )
                admin_action.save()
            except Exception as e:
                messages.error(request, f"Error on create the admin action.: {e}")
                return render(request, "a_school_admin/add-student.html", context)

            messages.success(request, "Student added successfully.")
            return redirect("students_mang_url")

        except Exception as e:
            messages.error(request, f"Failed to add student: {str(e)}")
            return render(request, "a_school_admin/add-student.html", context)

    return render(request, "a_school_admin/add-student.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_student(request, student_username):
    try:
        student = CustomUser.objects.get(username=student_username)
        student_profile = UserProfile.objects.get(user=student)
    except UserProfile.DoesNotExist:
        messages.error(request, "Student Doesn't Exist.")
        return redirect("student_mang_url")
    context = {"student_profile": student_profile}
    context.update(identify)

    if request.method == "POST":
        try:
            first_name = request.POST.get("first_name", "").strip()
            middle_name = request.POST.get("middle_name", "").strip()
            last_name = request.POST.get("last_name", "").strip()
            phone_number = request.POST.get("phone_number", "").strip()
            age = request.POST.get("age", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "").strip()
            profile_image = request.FILES.get("profile_image")

            has_changes = False
            changes = []

            if email != student.email:
                if not validate_email(email):
                    messages.error(request, "Invalid Email Format!")
                    return render(request, "a_school_admin/edit-students.html", context)
                if (
                    CustomUser.objects.filter(email=email)
                    .exclude(email=student.email)
                    .exists()
                ):
                    messages.error(request, "Email already exists.")
                    return render(request, "a_school_admin/edit-students.html", context)
                student.email = email
                changes.append("email")
                has_changes = True

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

            if not re.match(r"^\+?[0-9]{8,15}$", phone_number):
                messages.error(
                    request, "Invalid phone number format. Use +1234567890 format."
                )
                return render(request, "a_school_admin/edit-students.html", context)
            if phone_number != student.phone_number:
                student.phone_number = phone_number
                changes.append("phone number")
                has_changes = True

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

            if password and student_profile.password != password:
                student.set_password(password)
                student_profile.password = password
                changes.append("password")
                has_changes = True

            if profile_image and profile_image != student_profile:
                student_profile.user_pic = profile_image
                changes.append("profile image")
                has_changes = True

            if has_changes:
                student.save()
                student_profile.save()
                AdminAction.objects.create(
                    admin=request.user,
                    action=f"Edited Student ({student.first_name}): Updated {', '.join(changes)}",
                )
                messages.success(request, "Student updated successfully.")
            else:
                messages.info(request, "No changes detected.")

            return redirect("students_mang_url")

        except Exception as e:
            messages.error(request, f"Update failed: {str(e)}")
            return render(request, "a_school_admin/edit-students.html", context)

    return render(request, "a_school_admin/edit-students.html", context)


@user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
def add_students(request):
    REQUIRED_COLUMNS = [
        "first name",
        "middle name",
        "last name",
        "email",
        "age",
        "phone number",
        "gender",
        "class",
    ]
    context = {"required_columns": REQUIRED_COLUMNS, "errors": []}
    context.update(identify)
    emails = []

    if request.method == "POST":
        uploaded_file = request.FILES.get("file")
        if not uploaded_file or not uploaded_file.name.endswith((".xls", ".xlsx")):
            context["errors"].append("Please upload a valid Excel file.")
            return render(request, "a_school_admin/upload.html", context)

        try:
            df = pd.read_excel(
                uploaded_file, dtype={"phone number": str, "class": str}
            ).fillna("")
        except Exception as e:
            context["errors"].append(f"Error reading file: {e}")
            return render(request, "a_school_admin/upload.html", context)

        cols_lower = [c.lower() for c in df.columns]
        missing = [c for c in REQUIRED_COLUMNS if c.lower() not in cols_lower]
        if missing:
            context["errors"].append(f"Missing columns: {', '.join(missing)}")
            return render(request, "a_school_admin/upload.html", context)

        errors = []
        for idx, row in df.iterrows():
            line = idx + 2
            row_err = []

            def field(col):
                return str(row[col]).strip()

            empty = [c for c in REQUIRED_COLUMNS if not field(c)]
            if empty:
                row_err.append(f"Line {line}: Missing {', '.join(empty)}")

            class_name = field("class").upper()
            if not re.fullmatch(r"\d{1,2}[A-H]", class_name):
                row_err.append(f"Line {line}: Invalid class '{class_name}'")
            elif not Class.objects.filter(class_name=class_name).exists():
                row_err.append(f"Line {line}: Class '{class_name}' not found")

            try:
                age = int(field("age"))
                if not 4 <= age <= 80:
                    row_err.append(f"Line {line}: Age {age} out of range")
            except:
                row_err.append(f"Line {line}: Invalid age")

            phone = field("phone number")
            if not (phone.isdigit() and len(phone) <= 13):
                row_err.append(f"Line {line}: Invalid phone '{phone}'")

            g = field("gender").upper()
            if g not in ("M", "F", "MALE", "FEMALE"):
                row_err.append(f"Line {line}: Invalid gender '{g}'")

            for n in ["first name", "middle name", "last name"]:
                if not re.fullmatch(r"[A-Za-z\- ]+", field(n)):
                    row_err.append(f"Line {line}: Invalid {n}")

            email = field("email").lower()
            if not validate_email(email):
                row_err.append(f"Line {line}: Invalid email")
            elif CustomUser.objects.filter(email=email).exists():
                row_err.append(f"Line {line}: Email already exists.")
            else:
                if email not in emails:
                    emails.append(email)
                else:
                    row_err.append(f"Line {line}: Email should be unique.")

            if row_err:
                errors.extend(row_err)

        if errors:
            context["errors"] = errors
            return render(request, "a_school_admin/upload.html", context)

        try:
            with transaction.atomic():
                created = 0
                for idx, row in df.iterrows():

                    def field(col):
                        return str(row[col]).strip()

                    user = CustomUser(
                        first_name=field("first name"),
                        middle_name=field("middle name"),
                        last_name=field("last name"),
                        email=field("email").lower(),
                        age=int(field("age")),
                        gender=(
                            "male"
                            if field("gender").upper() in ["M", "MALE"]
                            else (
                                "female"
                                if field("gender").upper() in ["F", "FEMALE"]
                                else field("gender")
                            )
                        ),
                        phone_number=field("phone number"),
                        role="student",
                    )
                    password = generate_password(include_special_chars=False)
                    user.set_password(password)
                    user.save()

                    try:
                        user_profile = UserProfile.objects.create(
                            user=user,
                            user_pic=default_avatar_path,
                            password=password,
                        )
                    except Exception as e:
                        user.delete()
                        messages.error(request, f"Faild to create the profile: {e}")
                        return render(request, "a_school_admin/upload.html", context)

                    class_name = field("class").upper()
                    cls = Class.objects.get(class_name=class_name)
                    class_room, _ = ClassRoom.objects.get_or_create(class_name=cls)
                    class_room.students.add(user_profile)

                    created += 1

                AdminAction.objects.create(
                    admin=request.user, action=f"Bulk added {created} students"
                )
                messages.success(request, f"Successfully added {created} students")
                return redirect("students_mang_url")

        except Exception as e:
            context["errors"].append(f"System error: {e}")

    return render(request, "a_school_admin/upload.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def download_student_excel_template(request):
    columns = [
        "first name",
        "middle name",
        "last name",
        "email",
        "age",
        "phone number",
        "gender",
        "class",
    ]

    df = pd.DataFrame(columns=columns)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="student_template.xlsx"'

    df.to_excel(response, index=False)
    return response


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def download_students_excel(request):
    students = CustomUser.objects.filter(role="student")
    student_data = []
    for student in students:
        try:
            student_profile = UserProfile.objects.get(user=student)
        except UserProfile.DoesNotExist:
            continue
        student_data.append(
            {
                "first_name": student.first_name,
                "middle_name": student.middle_name,
                "last_name": student.last_name,
                "gender": student.gender,
                "age": student.age,
                "email": student.email,
                "password": UserProfile.objects.get(user=student).password,
            }
        )

    df = pd.DataFrame(student_data)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    buffer.seek(0)
    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="students.xlsx"'

    return response
