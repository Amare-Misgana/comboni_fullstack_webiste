from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from common.models import UserProfile, Message, CustomUser
from django.db.models import Q, Subquery, OuterRef


@user_passes_test(lambda user: user.is_authenticated and user.role=="teacher")
def teacher_dashboard(request):
    context = {
        "user_profile": UserProfile.objects.get(user=request.user),
    }
    return render(request, "a_teacher/dashboard.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role=="teacher")
def chat(request):
    # Get all users by role with latest profile
    students = CustomUser.objects.filter(role='student').annotate(
        latest_profile=Subquery(
            UserProfile.objects.filter(user=OuterRef('pk'))
            .order_by('-id').values('user_pic')[:1]
        )
    )
    
    teachers = CustomUser.objects.filter(role='teacher').exclude(id=request.user.id).annotate(
        latest_profile=Subquery(
            UserProfile.objects.filter(user=OuterRef('pk'))
            .order_by('-id').values('user_pic')[:1]
        )
    )
    
    admins = CustomUser.objects.filter(role='admin').annotate(
        latest_profile=Subquery(
            UserProfile.objects.filter(user=OuterRef('pk'))
            .order_by('-id').values('user_pic')[:1]
        )
    )

    # Get message partners for all roles
    teacher_profile = request.user.userprofile_set.first()
    message_partners = UserProfile.objects.filter(
        Q(received_messages__sender=teacher_profile) |
        Q(sent_messages__receiver=teacher_profile)
    ).distinct()

    return render(request, 'a_teacher/chat.html', {
        'students': students,
        'teachers': teachers,
        'admins': admins,
        'message_partners': message_partners,
    })