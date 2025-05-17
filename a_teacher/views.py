from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from common.models import UserProfile, CustomUser
from a_message.models import Message
from django.db.models import Q


@user_passes_test(lambda user: user.is_authenticated and user.role=="teacher")
def teacher_dashboard(request):
    context = {
        "user_profile": UserProfile.objects.get(user=request.user),
    }
    return render(request, "a_teacher/dashboard.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role=="teacher")
def chat(request):
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

    return render(request, 'a_teacher/chat.html', {
        'students': students,
        'teachers': teachers,
        'admins': admins,
        'latest_messages': latest_messages,
    })


def chatting(request):
    return render(request, "a_teacher/chatting.html")