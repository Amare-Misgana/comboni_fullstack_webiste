from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from common.models import UserProfile, CustomUser
from a_message.models import Message
from django.db.models import Q

# Global Variables for chat and chatting views 
identify = {
    'is_student': False,
    'is_teacher': True,
    'is_admin': False,
}

@user_passes_test(lambda user: user.is_authenticated and user.role=="teacher")
def teacher_dashboard(request):
    context = {
        "user_profile": UserProfile.objects.get(user=request.user),
    }
    context.update(identify)
    return render(request, "a_teacher/dashboard.html", context)



@user_passes_test(lambda u: u.is_authenticated and u.role == "teacher")
def chat(request):
    me = UserProfile.objects.get(user=request.user)

    students = UserProfile.objects.filter(user__role='student')
    teachers = UserProfile.objects.filter(user__role='teacher').exclude(pk=me.pk)
    admins   = UserProfile.objects.filter(user__role='admin')

    def attach_last_msg(qs):
        for peer in qs:
            peer.last_message = (
                Message.objects
                       .filter(Q(sender=me, receiver=peer) | Q(sender=peer, receiver=me))
                       .order_by('-timestamp')
                       .first()
            )
        return qs

    context = {
        'students': attach_last_msg(students),
        'teachers': attach_last_msg(teachers),
        'admins':   attach_last_msg(admins),
    }
    context.update(identify)
    return render(request, 'fragments/chat.html', context)


def get_room_name(user1, user2):
    users = sorted([str(user1).lower(), str(user2).lower()])
    return f"chat_{users[0]}-{users[1]}"


@user_passes_test(lambda u: u.is_authenticated and u.role == "teacher")
def chatting(request, username):
    me = UserProfile.objects.get(user=request.user) 
    students = UserProfile.objects.filter(user__role='student')
    teachers = UserProfile.objects.filter(user__role='teacher').exclude(id=me.id)
    admins   = UserProfile.objects.filter(user__role='admin')

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
    
    userprofile = UserProfile.objects.all()
    
    room_name = get_room_name(request.user.username, receiver.username)


    chat_messages = Message.objects.filter(
        Q(sender__user=request.user, receiver__user=receiver) |
        Q(sender__user=receiver, receiver__user=request.user)
    ).order_by('timestamp').distinct()
    context =  {
        'students': students,
        'teachers': teachers,
        'admins': admins,
        'latest_messages': latest_messages,
        'chats': chats,
        'room_name': room_name,
        'receiver': receiver,
        'receiver_profile': UserProfile.objects.get(user=receiver),
        'current_user': request.user,
        'other_user': receiver,
        'chat_messages': chat_messages,
        'userprofile': userprofile, 
    }
    context.update(identify)

    return render(request, 'fragments/chatting.html', context)