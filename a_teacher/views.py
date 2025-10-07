from django.http import Http404
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from common.models import (
    UserProfile,
    CustomUser,
    ClassRoom,
    ClassSubject,
    Class,
    Conduct,
    Material,
    Activity,
    Mark,
    ActivityCategory,
)
from .models import TeacherAction
from a_message.models import Message
from django.contrib import messages
from django.db.models import Q
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from common.utils import get_student_activities, get_student_activities_by_category

# Global Variables for chat and chatting views
identify = {
    "is_student": False,
    "is_teacher": True,
    "is_admin": False,
}


@user_passes_test(lambda user: user.is_authenticated and user.role == "teacher")
def teacher_dashboard(request):
    teacher_profile = UserProfile.objects.get(user=request.user)
    class_room = ClassRoom.objects.filter(room_teacher__user=request.user).first()

    teaching = ClassSubject.objects.filter(teacher=request.user)

    subject_list = []

    for _teaching in teaching:

        _teaching.subject in subject_list or subject_list.append(_teaching.subject)
    subjects = len(subject_list)

    total_students = (
        UserProfile.objects.filter(
            classroom_students__class_subjects__teacher=request.user,
            user__role="student",
        )
        .distinct()
        .count()
    )

    total_sections = (
        ClassSubject.objects.filter(teacher=request.user)
        .values("class_room")
        .distinct()
        .count()
    )

    # Students in the homeroom class (optional)
    # Error querying students from the database: 'NoneType' object has no attribute 'students'
    try:
        if class_room:
            students = list(class_room.students.select_related("user"))
    except Exception as e:
        messages.error(request, f"Error querying students from the database: {e}")
        return redirect("teachers_mang_url")
    if class_room:
        student_data = []
        for student in students:
            conduct = Conduct.objects.filter(
                student=student, teacher=teacher_profile
            ).first()
            if not conduct:
                conduct = Conduct.objects.create(
                    student=student, teacher=teacher_profile
                )
            student_data.append(
                {
                    "user": student.user,
                    "profile": student,
                    "conduct": conduct.conduct if conduct else "None",
                }
            )
    else:
        student_data = None

    # 🧠 Students the teacher teaches in any subject (not just homeroom)
    taught_students = (
        UserProfile.objects.filter(
            classroom_students__class_subjects__teacher=request.user,
            user__role="student",
        )
        .select_related("user")
        .distinct()
    )

    students_taught = []
    for student in taught_students:
        conduct = Conduct.objects.filter(
            student=student, teacher=teacher_profile
        ).first()
        class_room = ClassRoom.objects.filter(students=student).first()
        if not conduct:
            conduct = Conduct.objects.create(student=student, teacher=teacher_profile)
        students_taught.append(
            {
                "user": student.user,
                "profile": student,
                "conduct": conduct.conduct if conduct else "None",
                "class": class_room.class_name.class_name,
            }
        )

    context = {
        "user_profile": teacher_profile,
        "class_room": class_room,
        "students": student_data,
        "students_taught": students_taught,  # Added full list
        "subjects": subjects,
        "total_students": total_students,
        "total_sections": total_sections,
    }

    context.update(identify)
    return render(request, "a_teacher/dashboard.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "teacher")
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

    except CustomUser.DoesNotExist:
        messages.error(request, "Student can't be found!")
        return redirect("students_mang_url")

    conduct = Conduct.objects.filter(student__user=student).first()
    print(conduct.student)
    if not conduct:
        student_profile = UserProfile.objects.get(user=student)
        conduct = Conduct.objects.create(student=student_profile)
    context = {
        "student": student,
        "conduct": conduct,
        "student_profile": student_profile,
        "student_class": student_class,
        "teacher_user": True,
    }
    context.update(identify)
    return render(request, "a_school_admin/student-detail.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "teacher")
def edit_conduct(request, username):
    teacher_profile = get_object_or_404(
        UserProfile, user=request.user, user__role="teacher"
    )
    student_profile = get_object_or_404(
        UserProfile, user__username=username, user__role="student"
    )
    conduct_obj, _ = Conduct.objects.get_or_create(
        teacher=teacher_profile, student=student_profile
    )
    if request.method == "POST":
        new_val = request.POST.get("conduct")
        valid_vals = [choice[0] for choice in Conduct.CONDUCT_VALUES]
        if new_val in valid_vals:
            conduct_obj.conduct = new_val
            conduct_obj.save()
            messages.success(
                request, f"Conduct for {student_profile.username} set to “{new_val}”"
            )
        else:
            messages.error(request, "Invalid conduct value.")
        return redirect("edit_conduct_url", username=username)
    context = {
        "student": student_profile,
        "class_room": ClassRoom.objects.filter(room_teacher=teacher_profile).first(),
        "current": conduct_obj.conduct,
        "choices": Conduct.CONDUCT_VALUES,
    }
    context.update(identify)
    return render(request, "a_teacher/edit-conduct.html", context)


@user_passes_test(lambda u: u.is_authenticated and u.role == "teacher")
def chat(request):
    me = UserProfile.objects.get(user=request.user)

    students = UserProfile.objects.filter(user__role="student")
    teachers = UserProfile.objects.filter(user__role="teacher").exclude(pk=me.pk)
    admins = UserProfile.objects.filter(user__role="admin")

    def attach_last_msg(qs):
        for peer in qs:
            peer.last_message = (
                Message.objects.filter(
                    Q(sender=me, receiver=peer) | Q(sender=peer, receiver=me)
                )
                .order_by("-timestamp")
                .first()
            )
        return qs

    context = {
        "students": attach_last_msg(students),
        "teachers": attach_last_msg(teachers),
        "admins": attach_last_msg(admins),
    }
    context.update(identify)
    return render(request, "fragments/chat.html", context)


def get_room_name(user1, user2):
    users = sorted([str(user1).lower(), str(user2).lower()])
    return f"chat_{users[0]}-{users[1]}"


@user_passes_test(lambda u: u.is_authenticated and u.role == "teacher")
def chatting(request, username):
    me = UserProfile.objects.get(user=request.user)
    students = UserProfile.objects.filter(user__role="student")
    teachers = UserProfile.objects.filter(user__role="teacher").exclude(id=me.id)
    admins = UserProfile.objects.filter(user__role="admin")

    msgs = Message.objects.filter(Q(sender=me) | Q(receiver=me)).order_by("-timestamp")

    seen = set()
    latest_messages = []
    for m in msgs:
        other = m.receiver if m.sender == me else m.sender
        if other.id not in seen:
            seen.add(other.id)
            latest_messages.append(m)

    other = UserProfile.objects.get(user__username=username)

    chats = Message.objects.filter(
        Q(sender=me, receiver=other) | Q(sender=other, receiver=me)
    ).order_by("timestamp")

    try:
        receiver = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        raise Http404("User does not exist")

    userprofile = UserProfile.objects.all()

    room_name = get_room_name(request.user.username, receiver.username)

    chat_messages = (
        Message.objects.filter(
            Q(sender__user=request.user, receiver__user=receiver)
            | Q(sender__user=receiver, receiver__user=request.user)
        )
        .order_by("timestamp")
        .distinct()
    )
    context = {
        "students": students,
        "teachers": teachers,
        "admins": admins,
        "latest_messages": latest_messages,
        "chats": chats,
        "room_name": room_name,
        "receiver": receiver,
        "receiver_profile": UserProfile.objects.get(user=receiver),
        "current_user": request.user,
        "other_user": receiver,
        "chat_messages": chat_messages,
        "userprofile": userprofile,
    }
    context.update(identify)

    return render(request, "fragments/chatting.html", context)


@user_passes_test(lambda u: u.is_authenticated and u.role == "teacher")
def teacher_classes(request):
    taught = ClassSubject.objects.filter(teacher=request.user)

    stats = []
    for cs in taught:
        room = cs.class_room
        students_count = room.students.count()
        materials_count = Material.objects.filter(
            uploaded_by__user=request.user
        ).count()

        stats.append(
            {
                "class_name": room.class_name.class_name,
                "subject": cs.subject.subject_name,
                "total_students": students_count,
                "total_materials": Material.objects.filter(
                    uploaded_by__user=request.user,
                    class_name__class_name=room.class_name.class_name,
                ).count(),
            }
        )
    context = {"classes": stats}
    context.update(identify)
    return render(request, "a_teacher/teacher-classes.html", context)


@user_passes_test(lambda u: u.is_authenticated and u.role == "teacher")
def share_material(request, class_name):

    identify.update({"class_name": class_name})

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        file = request.FILES.get("file")

        try:
            class_object = Class.objects.get(class_name=class_name)
        except Exception as e:
            messages.error(request, f"Can't query class: {e}")
            return render(request, "a_teacher/share-material.html", identify)

        if not (title and file):
            messages.error(request, "Title and file are required.")
            return render(request, "a_teacher/share-material.html", identify)

        user_profile = UserProfile.objects.get(user=request.user)
        Material.objects.create(
            title=title,
            file=file,
            uploaded_by=user_profile,
            description=description,
            class_name=class_object,
        )

        messages.success(request, "Material shared successfully.")
        return redirect("materials_list_url")

    return render(request, "a_teacher/share-material.html", identify)


@user_passes_test(lambda u: u.is_authenticated and u.role == "teacher")
def view_class_teacher(request, class_name):
    # 1. Fetch the classroom
    class_room = get_object_or_404(ClassRoom, class_name__class_name=class_name)

    # 2. Ensure this teacher is assigned
    if not ClassSubject.objects.filter(
        class_room=class_room, teacher=request.user
    ).exists():
        messages.error(request, "You are not assigned to this class.")
        return redirect("teacher_home_url")

    # 3. Handle inline “Create Activity” POST
    if request.method == "POST":
        atype = request.POST.get("activity_category", "").strip()
        name = request.POST.get("activity_name", "").strip()
        max_score = request.POST.get("activity_max_score", "").strip()
        print(request.POST)
        for a in list(ActivityCategory.objects.filter(name=atype)):
            print(a)
        if max_score and int(max_score) > 120:
            messages.error(request, "Invalid max score.")
            return redirect("view_class_url", class_name=class_name)
        try:
            activity_category = ActivityCategory.objects.filter(name=atype).first()
            print(activity_category)
        except ActivityCategory.DoesNotExist:
            messages.error(request, "Invalid class name.")
            return redirect("view_class_url", class_name=class_name)
        if activity_category and name:
            profile = UserProfile.objects.get(user=request.user)
            subject = class_room.class_subjects.get(teacher=request.user).subject
            Activity.objects.create(
                class_room=class_room,
                subject=subject,
                teacher=profile,
                activity_category=activity_category,
                activity_name=name,
                max_score=max_score,
            )
            messages.success(request, "Activity created.")
            return redirect("view_class_url", class_name=class_name)
        else:
            messages.error(request, "All fields are required.")

    # 4. Gather data for rendering
    try:
        class_object = Class.objects.get(class_name=class_name)
    except Class.DoesNotExist:
        messages.error(request, f"Can't query class: {class_name}")
        return redirect("teacher_home_url")

    subjects = ClassSubject.objects.get(class_room=class_room, teacher=request.user)
    students = subjects.class_room.students.select_related("user").all()
    student_count = class_room.students.count()
    user_profile = UserProfile.objects.get(user=request.user)
    materials = Material.objects.filter(
        uploaded_by=user_profile, class_name=class_object
    )
    activities = Activity.objects.filter(class_room=class_room, teacher=user_profile)
    activities_list = list(ActivityCategory.objects.order_by("name"))

    context = {
        "class_room": class_room,
        "subjects": subjects,
        "student_count": student_count,
        "materials": materials,
        "students": students,
        "activities": activities,
        "activities_list": activities_list,
    }
    context.update(identify)

    return render(request, "a_teacher/view-class.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "teacher")
def activities_list(request, class_name):
    room = get_object_or_404(ClassRoom, class_name__class_name=class_name)

    # ensure teacher teaches here
    if not room.class_subjects.filter(teacher=request.user).exists():
        messages.error(request, "You’re not assigned to that class.")
        return redirect("teacher_home_url")

    # only activities this teacher created in this class
    profile = UserProfile.objects.get(user=request.user)
    activities = Activity.objects.filter(class_room=room, teacher=profile)

    return render(
        request,
        "a_teacher/activities-list.html",
        {
            "class_room": room,
            "activities": activities,
        },
    )


@user_passes_test(lambda u: u.is_authenticated and u.role == "teacher")
def assign_marks(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    teacher_profile = UserProfile.objects.get(user=request.user)

    if activity.teacher != teacher_profile:
        messages.error(request, "Not authorized to grade this activity.")
        return redirect("teacher_dashboard_url")

    # fetch your students + existing scores…
    activity_catagory = ActivityCategory.objects.filter(name="Final Exam").first()
    students = list(activity.class_room.students.select_related("user"))
    for student in students:
        print(get_student_activities_by_category(student, activity_catagory))
        print("hi")

    existing = {m.student_id: m.score for m in activity.marks.all()}
    for st in students:
        st.score = existing.get(st.id, "")

    if request.method == "POST":
        updated = False
        had_error = False

        for st in students:
            val = request.POST.get(f"score_{st.id}", "").strip()
            orig = str(existing.get(st.id, ""))

            if not val or val == orig:
                continue

            # quick Decimal check
            try:
                Decimal(val)
            except InvalidOperation:
                messages.error(
                    request, f"“{val}” is not a valid number for {st.user.first_name}."
                )
                had_error = True
                continue

            # try saving
            try:
                Mark.objects.update_or_create(
                    activity=activity,
                    student=st,
                    defaults={"score": val},
                )
            except ValidationError as e:
                messages.error(request, f"{st.user.first_name}: {e.messages[0]}")
                had_error = True
            else:
                updated = True

        if had_error:
            # re-render so errors are visible
            return render(
                request,
                "a_teacher/assign-marks.html",
                {
                    "activity": activity,
                    "students": students,
                    **identify,
                },
            )

        if updated:
            messages.success(request, "Marks saved.")
        else:
            messages.info(request, "No changes detected; nothing to save.")

        return redirect(
            "view_class_url", class_name=activity.class_room.class_name.class_name
        )

    return render(
        request,
        "a_teacher/assign-marks.html",
        {
            "activity": activity,
            "students": students,
            **identify,
        },
    )


@user_passes_test(lambda user: user.is_authenticated and user.role == "teacher")
def view_activity_marks(request, activity_id):
    activity = get_object_or_404(Activity, pk=activity_id)
    try:
        marks = Mark.objects.filter(activity=activity)
    except Exception as e:
        messages.error(request, "Can't query marks.")
        return redirect("teacher_dashboard_url")

    teacher_profile = UserProfile.objects.get(user=request.user)

    if activity.teacher != teacher_profile:
        messages.error(request, "Not authorized to view these marks.")
        return redirect("teacher_dashboard_url")

    # Fetch all marks for this activity
    marks_qs = Mark.objects.filter(activity=activity).select_related("student__user")
    # Map student_id → score (or None)
    scores = {m.student.id: m.score for m in marks_qs}

    # Get full student list
    students = activity.class_room.students.select_related("user").all()

    context = {
        "activity": activity,
        "students": students,
        "scores": scores,
        "marks": marks,
        "activites_list": list(ActivityCategory.objects.order_by("name")),
    }
    context.update(identify)

    return render(request, "a_teacher/view-marks.html", context)
