from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from common.models import (
    UserProfile,
    ClassRoom,
    Class,
    Subject,
    ClassSubject,
    CustomUser,
)
from django.db.models.functions import Length
import re

identify = {
    "is_admin": True,
    "is_teacher": False,
    "is_student": False,
}


# ===================  Classes View ==================


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def class_mang(request):
    context = {
        "classes": Class.objects.all().order_by(Length("class_name"), "class_name"),
        "class_rooms": ClassRoom.objects.all().order_by(
            Length("class_name__class_name"), "class_name__class_name"
        ),
        "users": UserProfile.objects.all(),
    }
    context.update(identify)
    return render(request, "a_school_admin/class-mang.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_class(request, class_name):
    context = {}
    context.update(identify)
    return render(request, "a_school_admin/edit-class.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def create_classes(request):
    if request.method == "POST":
        class_names_input = request.POST.get("class_names", "")
        raw_names = [
            name.strip() for name in class_names_input.split(",") if name.strip()
        ]
        processed_names = []

        for name in raw_names:
            match = re.match(r"^(\d+)([a-zA-Z])$", name)
            if match:
                grade = match.group(1)
                section = match.group(2).upper()
                processed_names.append(f"{grade}{section}")
            else:
                messages.warning(
                    request, f"'{name}' is not a valid class format (e.g. 11A)"
                )

        if not processed_names:
            messages.error(request, "No valid class names provided.")
            return redirect("create_classes_url")

        unique_names = set(processed_names)

        existing = set(
            Class.objects.filter(class_name__in=unique_names).values_list(
                "class_name", flat=True
            )
        )

        new_classes = [name for name in unique_names if name not in existing]
        duplicates = [name for name in unique_names if name in existing]

        for name in new_classes:
            Class.objects.create(class_name=name)

        if new_classes:
            messages.success(
                request, f"Successfully created {len(new_classes)} classes."
            )
        if duplicates:
            messages.warning(
                request,
                f"{len(duplicates)} classes already exist: {', '.join(duplicates)}",
            )
        ClassRoom.objects.create()

        return render(
            request,
            "a_school_admin/create-classes.html",
            {
                "classes": Class.objects.all(),
                "is_admin": True,
                "is_teacher": False,
                "is_student": False,
            },
        )
    context = {
        "classes": Class.objects.all().order_by(Length("class_name"), "class_name")
    }
    context.update(identify)
    return render(request, "a_school_admin/create-classes.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def class_detail(request, class_name):
    try:
        class_name_obj = get_object_or_404(Class, class_name=class_name)
        class_room, created = ClassRoom.objects.get_or_create(class_name=class_name_obj)
        if not class_room.class_name:
            messages.error(request, "Empty class name")
        students = list(class_room.students.all())
    except Exception as e:
        messages.error(request, f"Error querying data from the database: {e}")
        return redirect("class_mang_url")

    assigned_subjects = ClassSubject.objects.filter(class_room=class_room)
    assigned_subject_ids = assigned_subjects.values_list("subject", flat=True)
    assigned_teacher_ids = assigned_subjects.values_list("teacher", flat=True)

    teachers = CustomUser.objects.filter(role="teacher").exclude(
        id__in=assigned_teacher_ids
    )
    subjects = Subject.objects.exclude(id__in=assigned_subject_ids)

    class_object = class_room

    context = {
        "assigned_subjects": assigned_subjects,
        "students": students,
        "class_room": class_room,
        "teachers": teachers,
        "subjects": subjects,
        "class_object": class_object,
    }
    context.update(identify)
    return render(request, "a_school_admin/class-detail.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def remove_homeroom_teacher(request, teacher, class_name):
    if request.method == "POST":
        class_room = get_object_or_404(ClassRoom, room_teacher__user__username=teacher)
        class_room.room_teacher = None
        class_room.save()
        messages.success(request, "Successfully removed homeroom teacher.")
    return redirect("class_detail_url", class_name=class_name)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def delete_assigned_subjects(request, subject, classroom_id):
    try:
        class_room = get_object_or_404(ClassRoom, id=classroom_id)
        class_name = class_room.class_name.class_name
        classroom = class_room.class_name
        subject_model = ClassSubject.objects.get(
            class_room__class_name=class_name, subject__subject_name=subject
        )
    except ClassSubject.DoesNotExist:
        messages.error(request, "This class doesn't contain any subjects")
        return redirect("class_detail_url", class_name=classroom)
    if request.method == "POST":
        if hasattr(subject_model, "subject"):
            if subject_model.subject.subject_name == subject:
                subject_model.delete()
                messages.success(request, "Subject deleted successfully.")
                return redirect("class_detail_url", class_name=classroom)
            else:
                messages.error(request, "Invalid subject.")
                return redirect("class_detail_url", class_name=classroom)
        else:
            messages.error(request, "Subject model doesn't have a subject attribute.")

    return redirect("class_detail_url", class_name=classroom)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_homeroom_teacher(request, class_name):
    class_room = get_object_or_404(ClassRoom, class_name__class_name=class_name)
    assigned_teachers = list(
        ClassRoom.objects.exclude(room_teacher__isnull=True).values_list(
            "room_teacher", flat=True
        )
    )

    available_teachers = UserProfile.objects.filter(user__role="teacher").exclude(
        user__id__in=assigned_teachers
    )

    if request.method == "POST":
        teacher = request.POST.get("teacher")
        if not teacher:
            messages.error(request, "Please select a teacher.")
            return redirect("add_homeroom_url", class_name=class_name)

        try:
            teacher = UserProfile.objects.get(
                user__username=teacher, user__role="teacher"
            )
        except UserProfile.DoesNotExist:
            messages.error(request, "Selected teacher not found.")
            return redirect("add_homeroom_url", class_name=class_name)

        class_room.room_teacher = teacher
        class_room.save()
        messages.success(request, f"{teacher.username} set as homeroom teacher.")
        return redirect("class_detail_url", class_name=class_name)

    context = {
        "class_room": class_room,
        "available_teachers": available_teachers,
        "class_name_url": class_name,
    }
    context.update(identify)
    return render(request, "a_school_admin/add-homeroom.html", context)


@user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
def edit_class(request, class_name):
    pass


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def create_subjects(request):
    if request.method == "POST":
        subject_names_input = request.POST.get("subject_names", "")
        is_graded = request.POST.get("is_graded") == "on"
        raw_names = [
            name.strip() for name in subject_names_input.split(",") if name.strip()
        ]
        unique_names = set(raw_names)

        existing = set(
            Subject.objects.filter(subject_name__in=unique_names).values_list(
                "subject_name", flat=True
            )
        )

        new_subjects = [name for name in unique_names if name not in existing]
        duplicates = [name for name in unique_names if name in existing]

        for name in new_subjects:
            Subject.objects.create(subject_name=name, is_graded=is_graded)

        if new_subjects:
            messages.success(
                request, f"Successfully created {len(new_subjects)} subjects."
            )
        if duplicates:
            messages.warning(
                request,
                f"{len(duplicates)} subjects already exist: {', '.join(duplicates)}",
            )

        return render(
            request,
            "a_school_admin/create-subjects.html",
            {
                "subjects": Subject.objects.all(),
                "is_admin": True,
                "is_teacher": False,
                "is_student": False,
            },
        )

    return render(
        request,
        "a_school_admin/create-subjects.html",
        {
            "subjects": Subject.objects.all().order_by("subject_name"),
            "is_admin": True,
            "is_teacher": False,
            "is_student": False,
        },
    )


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_subject(request, subject_name):
    subject = get_object_or_404(Subject, subject_name=subject_name)

    if request.method == "POST":
        new_name = request.POST.get("subject_name", "").strip()
        is_graded = request.POST.get("is_graded") == "on"

        if new_name:
            subject.subject_name = new_name
            subject.is_graded = is_graded
            subject.save()
            messages.success(request, "Subject updated successfully.")
            return redirect("add_subjects_url")
        else:
            messages.error(request, "Subject name cannot be empty.")

    context = {"subject": subject}
    context.update(identify)
    return render(request, "a_school_admin/edit-subject.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def delete_subject(request, subject_name):
    subject = get_object_or_404(Subject, subject_name=subject_name)
    subject.delete()
    messages.success(request, "Subject deleted successfully.")
    return redirect("add_subjects_url")


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def assign_subject_view(request, classroom_id):
    class_room = get_object_or_404(ClassRoom, id=classroom_id)
    classroom = class_room.class_name
    assigned_teacher_ids = ClassSubject.objects.values_list("teacher", flat=True)

    if request.method == "POST":
        subject_id = request.POST.get("subject")
        teacher_username = request.POST.get("teacher")

        if not subject_id:
            messages.error(request, "Please select a subject.")
            return redirect("class_detail_url", class_name=classroom)

        if not teacher_username:
            messages.error(request, "Please select a teacher.")
            return redirect("class_detail_url", class_name=classroom)

        try:
            subject_model = Subject.objects.get(id=subject_id)
        except Subject.DoesNotExist:
            messages.error(request, "Subject doesn't exist.")
            return redirect("class_detail_url", class_name=classroom)

        try:
            teacher_model = CustomUser.objects.get(username=teacher_username)
        except CustomUser.DoesNotExist:
            messages.error(request, "Teacher not found.")
            return redirect("class_detail_url", class_name=classroom)

        if teacher_model.id in assigned_teacher_ids:
            messages.error(request, "Teacher already exists.")
            return redirect("class_detail_url", class_name=classroom)

        if ClassSubject.objects.filter(subject=subject_model).exists():
            messages.error(request, "Subject already assigned.")
            return redirect("class_detail_url", class_name=classroom)

        try:
            ClassSubject.objects.create(
                class_room=class_room, subject=subject_model, teacher=teacher_model
            )
            messages.success(request, "Subject assigned successfully.")
        except Exception as e:
            messages.error(request, f"Failed to assign subject: {e}")

        return redirect("class_detail_url", class_name=classroom)

    return redirect("class_detail_url", class_name=classroom)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def classroom_add(request):
    classes = Class.objects.all()
    teachers = UserProfile.objects.filter(role="teacher")
    students = UserProfile.objects.filter(role="student")

    if request.method == "POST":
        class_name = request.POST["class_name"]
        teacher_id = request.POST.get("room_teacher")
        student_ids = request.POST.getlist("students")

        cls = Class.objects.get(class_name=class_name)
        room = ClassRoom.objects.create(
            class_name=cls, room_teacher_id=teacher_id or None
        )

        if student_ids:
            room.students.set(student_ids)

        return redirect("detail_classroom_url", pk=class_name)

    context = {
        "classes": classes,
        "teachers": teachers,
        "students": students,
    }
    context.update(identify)
    return render(request, "a_school_admin/add-classroom.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def classroom_add(request):
    classes = Class.objects.all()
    teachers = UserProfile.objects.filter(role="teacher")
    students = UserProfile.objects.filter(role="student")

    if request.method == "POST":
        class_name = request.POST["class_name"]
        teacher_id = request.POST.get("room_teacher")
        student_ids = request.POST.getlist("students")

        cls = Class.objects.get(class_name=class_name)
        room = ClassRoom.objects.create(
            class_name=cls, room_teacher_id=teacher_id or None
        )

        if student_ids:
            room.students.set(student_ids)

        return redirect("classroom_detail_url", pk=class_name)

    context = {
        "classes": classes,
        "teachers": teachers,
        "students": students,
    }
    context.update(identify)
    return render(request, "a_school_admin/add-classroom.html", context)
