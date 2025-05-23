from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.http import Http404
from a_message.models import Message
from django.db.models import Q
from .models import AdminAction, News
from common.models import UserProfile, CustomUser, ClassRoom, Class
import json

# ==================  HOME ==================


identify = {
    "is_admin": True,
    "is_teacher": False,
    "is_student": False,
}


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
            "male": class_students.filter(user__gender="male").count(),
            "female": class_students.filter(user__gender="female").count()
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


    data = [
            {
                "data": request.user.phone_number,
                "name": "Phone Number"
            },
            {
                "data": request.user.email,
                "name": "Email"
            }
        ]

    context = {
        "user_profile": user_profile,
        "students_amount": students.count(),
        "teachers_amount": teachers.count(),
        "classes_amount": len(classes),
        "sections_amount": classrooms.count(),  # Since ClassRoom is the section
        "classes": sorted({classroom.class_name.class_name[:-1] for classroom in classrooms}),  # Extract grade levels
        'action_profiles': action_profiles,  # Implement your action profiles logic
        "gender_json": json.dumps(grades),
        "class_json": json.dumps(classes_json),
        "datas": data,
    }
    context.update(identify)
    
    return render(request, "a_school_admin/dashboard.html", context)

# =================== Material View =================




@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def materials(request):
    pass

# =================== Chat View =================



@user_passes_test(lambda user: user.is_authenticated and user.role=="admin")
def chat(request):
    me = UserProfile.objects.get(user=request.user)

    teachers = UserProfile.objects.filter(user__role='teacher')
    admins   = UserProfile.objects.filter(user__role='admin').exclude(pk=me.pk)

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
        'teachers': attach_last_msg(teachers),
        'admins':   attach_last_msg(admins),
    }
    context.update(identify)
    return render(request, 'fragments/chat.html', context)

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

    chat_messages = Message.objects.filter(
        Q(sender__user=request.user, receiver__user=receiver) |
        Q(sender__user=receiver, receiver__user=request.user)
    ).order_by('timestamp').distinct()

    context = {
        'students': students,
        'teachers': teachers,
        'admins': admins,
        'latest_messages': latest_messages,
        'chats': chats,
        'room_name': room_name,
        'receiver': receiver,
        'current_user': request.user, 
        'other_user': receiver,
        'chat_messages': chat_messages,
    }
    context.update(identify)
    return render(request, 'fragments/chatting.html', context)

@user_passes_test(lambda user: user.is_authenticated and user.role=="admin")
def add_news(request):
    if request.method == 'POST':
        photo       = request.FILES.get('photo')
        header      = request.POST.get('header', '').strip()
        description = request.POST.get('description', '').strip()

        if not (photo and header and description):
            messages.error(request, "All fields are required.")
            return render(request, 'add_news.html')

        n = News(photo=photo, header=header, description=description)
        n.save()
        AdminAction.objects.create(
            admin=request.user,
            action=f"Added News ({n.header})"
        )
        messages.success(request, "News item added!")

    return render(request, 'a_school_admin/add-news.html', identify)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def all_news_view(request):
    news_qs = News.objects.all()
    news_list = []

    for item in news_qs:
        news_list.append({
            'id': item.id,
            'title': item.header,
            'description': item.description,
            'image_src': item.photo.url,
            'date': item.created_at.strftime('%B %d, %Y'),
            'url': f'/news/{item.id}/'  # or use `reverse('view_news', args=[item.id])`
        })

    context = {
        'news_list': news_list,
        'is_admin': True  # or check dynamically if needed
    }
    return render(request, 'a_school_admin/admin-news.html', context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_news(request, id):
    try:
        news = News.objects.get(id=id)
    except News.DoesNotExist:
        messages.error(request, f"Can't find the news.")
        return redirect('all_news_url')
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('photo')
        if title and description:
            news.title = title
            news.description = description
            if image:
                news.image_src = image
            news.save()
            return redirect('all_news_url')
    context = {'news': news}
    context.update(identify)
    return render(request, 'a_school_admin/edit-news.html', context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def delete_news(request, id):
    news = get_object_or_404(News, pk=id)
    if request.method == 'POST':
        news.delete()
        return redirect('all_news')
    context = {'news': news}
    context.update(identify)
    return render(request, 'a_school_admin/delete-news.html', context)


def view_news(request, id):
    news = get_object_or_404(News, pk=id)
    context = {'news': news}
    context.update(identify)
    return render(request, 'a_school_admin/view-news.html', context)











