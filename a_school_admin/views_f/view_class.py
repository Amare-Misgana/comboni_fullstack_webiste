from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from common.models import UserProfile, ClassRoom, Class, Subject, ClassSubject, CustomUser
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
        "classes": Class.objects.all().order_by(Length('class_name'), 'class_name'),
        "class_rooms": ClassRoom.objects.all().order_by(Length('class_name__class_name'), 'class_name__class_name'),
        "users": UserProfile.objects.all(),
    }
    context.update(identify)
    return render(request, "a_school_admin/class-mang.html", context)

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_class(request, class_name):
    context = {

    }
    context.update(identify)
    return render(request, "a_school_admin/edit-class.html", context)



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
            'classes': Class.objects.all(),
            "is_admin": True,
            "is_teacher": False,
            "is_student": False,
        })
    context = {
        'classes': Class.objects.all().order_by(Length('class_name'), 'class_name')
    }
    context.update(identify)
    return render(request, 'a_school_admin/create-classes.html', context)


@user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
def class_detail(request, class_name):
    teachers = CustomUser.objects.filter(role="teacher")
    subjects = Subject.objects.all()
    try:
        class_name = get_object_or_404(Class, class_name=class_name)
        class_room = get_object_or_404(ClassRoom, class_name=class_name)
        if not class_room.class_name:
            messages.error(request, "Empty class name")
        students = list(class_room.students.all())
    except Exception as e:
        messages.error(request, f"Error quering data from the database: {e}")
        return redirect("class_mang_url")
    
    assigned_subjects = ClassSubject.objects.filter(class_room__class_name__class_name=class_name)

    print(assigned_subjects)
    
    class_object = ClassRoom.objects.get(class_name__class_name=class_name)

    context = {
        "students": students,
        "class_room": class_room,
        "teachers": teachers,
        "subjects": subjects,
        "class_object": class_object,
        "students": class_object.students.all(),
    }
    context.update(identify)
    return render(request, 'a_school_admin/class-detail.html', context)

@user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
def edit_class(request, class_name):
    pass


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def create_subjects(request):
    if request.method == 'POST':
        subject_names_input = request.POST.get('subject_names', '')
        is_graded = request.POST.get('is_graded') == 'on'
        raw_names = [name.strip() for name in subject_names_input.split(',') if name.strip()]
        unique_names = set(raw_names)

        existing = set(Subject.objects.filter(
            subject_name__in=unique_names
        ).values_list('subject_name', flat=True))

        new_subjects = [name for name in unique_names if name not in existing]
        duplicates = [name for name in unique_names if name in existing]

        for name in new_subjects:
            Subject.objects.create(subject_name=name, is_graded=is_graded)

        if new_subjects:
            messages.success(request, f"Successfully created {len(new_subjects)} subjects.")
        if duplicates:
            messages.warning(request, f"{len(duplicates)} subjects already exist: {', '.join(duplicates)}")

        return render(request, 'a_school_admin/create-subjects.html', {
            'subjects': Subject.objects.all(),
            "is_admin": True,
            "is_teacher": False,
            "is_student": False,

        })

    return render(request, 'a_school_admin/create-subjects.html', {
        'subjects': Subject.objects.all().order_by('subject_name'),
        "is_admin": True,
        "is_teacher": False,
        "is_student": False,
    })

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_subject(request, subject_name):
    subject = get_object_or_404(Subject, subject_name=subject_name)

    if request.method == 'POST':
        new_name = request.POST.get('subject_name', '').strip()
        is_graded = request.POST.get('is_graded') == 'on'

        if new_name:
            subject.subject_name = new_name
            subject.is_graded = is_graded
            subject.save()
            messages.success(request, "Subject updated successfully.")
            return redirect('add_subjects_url')
        else:
            messages.error(request, "Subject name cannot be empty.")

    context = {'subject': subject}
    context.update(identify)
    return render(request, 'a_school_admin/edit-subject.html', context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def delete_subject(request, subject_name):
    subject = get_object_or_404(Subject, subject_name=subject_name)
    subject.delete()
    messages.success(request, "Subject deleted successfully.")
    return redirect('add_subjects_url')

@user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
def assign_subject_view(request, classroom_id):
    classroom = get_object_or_404(ClassRoom, id=classroom_id)

    if request.method == 'POST':
        selected = request.POST.getlist('students')
        if not selected:
            messages.error(request, "Please select at least one student.")
        else:
            for sid in selected:
                student = get_object_or_404(CustomUser, id=sid, role='student')
                classroom.students.add(UserProfile.objects.get(user=student))
            messages.success(request, f"Assigned {len(selected)} student(s).")
        return redirect('classroom_detail', class_name=classroom.class_name.class_name)

    return redirect('classroom_detail', class_name=classroom.class_name.class_name)


@user_passes_test(lambda u: u.is_authenticated and u.role == "admin")
def defined_class(request, defined_class_room):
    pass

