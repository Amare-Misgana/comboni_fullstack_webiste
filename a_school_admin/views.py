from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import Http404
from a_message.models import Message
from django.db.models import Q
from .models import AdminAction
from common.models import UserProfile, CustomUser, ClassRoom, Class
import json

# ==================  HOME ==================

@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def school_admin_dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    
    students = CustomUser.objects.filter(role="student")
    teachers = CustomUser.objects.filter(role="teacher")
    classes = sorted(set(int(item[:-1]) for item in Class.objects.values_list("class_name", flat=True)))
    classrooms = ClassRoom.objects.select_related('class_name', 'room_teacher').prefetch_related('students')
    
    grades = {}
    for classroom in classrooms:
        class_students = classroom.students.all()
        grades[classroom.class_name.class_name] = {
            "male": class_students.filter(gender="male").count(),
            "female": class_students.filter(gender="female").count()
        }
    
    classes_json = {
        "classes": [str(classroom.class_name) for classroom in classrooms],
        "data": [{
            "class": str(classroom.class_name),
            "male": grades[str(classroom.class_name)]["male"],
            "female": grades[str(classroom.class_name)]["female"]
        } for classroom in classrooms]
    }
    admin_actions = AdminAction.objects.select_related('admin').all().order_by('-timestamp')
    admin_profiles = UserProfile.objects.select_related('user').all()

    action_profiles = []
    for action in admin_actions:
        profile = next((p for p in admin_profiles if p.user == action.admin), None)
        if profile:
            action_profiles.append((action, profile))

    context = {
        "user_profile": user_profile,
        "students_amount": students.count(),
        "teachers_amount": teachers.count(),
        "classes_amount": len(classes),
        "sections_amount": classrooms.count(),  # Since ClassRoom is the section
        "classes": sorted({classroom.class_name.class_name[:-1] for classroom in classrooms}),  # Extract grade levels
        'action_profiles': action_profiles,  # Implement your action profiles logic
        "gender_json": json.dumps(grades),
        "class_json": json.dumps(classes_json)
    }
    
    return render(request, "a_school_admin/dashboard.html", context)

# =================== Material View =================




@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def materials(request):
    pass

# =================== Chat View =================

@user_passes_test(lambda user: user.is_authenticated and user.role=="admin")
def chat(request):
    me = UserProfile.objects.get(user=request.user)
    students = UserProfile.objects.filter(user__role='student')
    teachers = UserProfile.objects.filter(user__role='teacher')
    admins   = UserProfile.objects.filter(user__role='admin').exclude(id=me.id)

    msgs = Message.objects.filter(
        Q(sender=me) | Q(receiver=me)
    ).order_by('-timestamp')

    seen = set()
    latest_messages = []
    for m in msgs:
        other = m.receiver if m.sender == me else m.sender
        if other.id not in seen:
            seen.add(other.id)
            latest_messages.append(m)

    return render(request, 'a_school_admin/chat.html', {
        'students': students,
        'teachers': teachers,
        'admins': admins,
        'latest_messages': latest_messages,
    })

def get_room_name(user1, user2):
    users = sorted([str(user1).lower(), str(user2).lower()])
    return f"chat_{users[0]}-{users[1]}"


@user_passes_test(lambda user: user.is_authenticated and user.role=="admin")
def chatting(request, username):
    me = UserProfile.objects.get(user=request.user) 
    students = UserProfile.objects.filter(user__role='student')
    teachers = UserProfile.objects.filter(user__role='teacher')
    admins   = UserProfile.objects.filter(user__role='admin').exclude(id=me.id)

    msgs = Message.objects.filter(
        Q(sender=me) | Q(receiver=me)
    ).order_by('-timestamp')

    seen = set()
    latest_messages = []
    for m in msgs:
        other = m.receiver if m.sender == me else m.sender
        if other.id not in seen:
            seen.add(other.id)
            latest_messages.append(m)

    other = UserProfile.objects.get(user__username=username)

    chats = Message.objects.filter(
        Q(sender=me,    receiver=other) |
        Q(sender=other, receiver=me)
    ).order_by('timestamp')

    try:
        receiver = CustomUser.objects.get(username=username)
    except CustomUser.DoesNotExist:
        raise Http404("User does not exist")
    
    room_name = get_room_name(request.user.username, receiver.username)
    print("\n\n\n\n\n")
    print(room_name)
    print("\n\n\n\n\n")

    chat_messages = Message.objects.filter(
        Q(sender__user=request.user, receiver__user=receiver) |
        Q(sender__user=receiver, receiver__user=request.user)
    ).order_by('timestamp').distinct()

    return render(request, 'a_school_admin/chatting.html', {
        'students': students,
        'teachers': teachers,
        'admins': admins,
        'latest_messages': latest_messages,
        'chats': chats,
        'room_name': room_name,
        'receiver': receiver,
        'current_user': request.user,  # For template context
        'other_user': receiver,
        'chat_messages': chat_messages,
    })







