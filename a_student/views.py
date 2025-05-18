from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from common.models import UserProfile, CustomUser
from a_message.models import Message
from django.db.models import Q


@user_passes_test(lambda user: user.is_authenticated and user.role=="student")
def student_dashboard(request):
    context = {
        "user_profile": UserProfile.objects.get(user=request.user),
    }
    return render(request, "a_student/dashboard.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role=="student")
def chat(request):
    me = UserProfile.objects.get(user=request.user)
    students = UserProfile.objects.filter(user__role='student').exclude(id=me.id)
    teachers = UserProfile.objects.filter(user__role='teacher')

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

    return render(request, 'a_student/chat.html', {
        'students': students,
        'teachers': teachers,
        'latest_messages': latest_messages,
    })

def get_room_name(user1, user2):
    users = sorted([str(user1).lower(), str(user2).lower()])
    return f"chat_{users[0]}-{users[1]}"


@user_passes_test(lambda user: user.is_authenticated and user.role=="student")
def chatting(request, username):
    me = UserProfile.objects.get(user=request.user) 
    students = UserProfile.objects.filter(user__role='student').exclude(id=me.id)
    teachers = UserProfile.objects.filter(user__role='teacher')

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



    chat_messages = Message.objects.filter(
        Q(sender__user=request.user, receiver__user=receiver) |
        Q(sender__user=receiver, receiver__user=request.user)
    ).order_by('timestamp').distinct()

    return render(request, 'a_student/chatting.html', {
        'students': students,
        'teachers': teachers,
        'latest_messages': latest_messages,
        'chats': chats,
        'room_name': room_name,
        'receiver': receiver,
        'current_user': request.user,
        'other_user': receiver,
        'chat_messages': chat_messages,
    })
@user_passes_test(lambda user: user.is_authenticated and user.role=="student")
def material(request):
    pass