from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
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
        if not classroom.class_name:
            continue
        class_students = classroom.students.all()
        grades[str(classroom.class_name)] = {
            "male": class_students.filter(user__gender="male").count(),
            "female": class_students.filter(user__gender="female").count()
        }

    classes_json = {
        "classes": [str(c.class_name) for c in classrooms if c.class_name],
        "data": [
            {
                "class": str(c.class_name),
                "male": grades.get(str(c.class_name), {}).get("male", 0),
                "female": grades.get(str(c.class_name), {}).get("female", 0)
            }
            for c in classrooms if c.class_name
        ]
    }

    admin_actions = AdminAction.objects.select_related('admin').all().order_by('-timestamp')
    admin_profiles = UserProfile.objects.select_related('user').all()

    action_profiles = []
    for action in admin_actions:
        profile = next((p for p in admin_profiles if p.user == action.admin), None)
        if profile:
            action_profiles.append((action, profile))

    data = [
        {"data": request.user.phone_number, "name": "Phone Number"},
        {"data": request.user.email, "name": "Email"}
    ]

    context = {
        "user_profile": user_profile,
        "students_amount": students.count(),
        "teachers_amount": teachers.count(),
        "classes_amount": len(classes),
        "sections_amount": classrooms.count(),
        "class": sorted({c.class_name.class_name[:-1] for c in classrooms if c.class_name}),
        "action_profiles": action_profiles,
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
        'receiver_profile': UserProfile.objects.get(user=receiver),
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

        news = News(photo=photo, header=header, description=description)
        news.save()
        student_emails = CustomUser.objects.filter(role="student") \
                                           .values_list("email", flat=True)

        subject = f"📢 New News: {news.header}"
        plain_message = news.description
        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            body {{
              margin:0;
              padding:20px 0;
              background-color: var(--primary);
              font-family: Arial, Helvetica, sans-serif;
              color: var(--primary-text);
            }}
            .container {{
              max-width:600px;
              margin:0 auto;
              background: var(--background);
              border-radius: var(--card-radius);
              box-shadow: 0 2px 4px var(--box-shadow);
              overflow: hidden;
            }}
            .header {{
              background: var(--primaryD);
              padding: 20px;
              text-align: center;
            }}
            .header h1 {{
              margin:0;
              color:#fff;
              font-size:32px;
            }}
            .content {{
              padding: 30px;
              color: var(--secondary-text);
              line-height:1.5;
            }}
            .button {{
              display:inline-block;
              margin:20px 0;
              padding:12px 24px;
              background: var(--primary);
              color:#fff !important;
              text-decoration:none;
              border-radius:4px;
              transition: var(--transition);
            }}
            .button:hover {{
              background: var(--primaryL);
            }}
            .footer {{
              font-size:12px;
              color: var(--last-text);
              text-align:center;
              padding: 10px;
            }}
          </style>
          <title>{news.header}</title>
        </head>
        <body>
          <center>
            <div class="container">
              <div class="header">
                <h1>📢 {news.header}</h1>
              </div>
              <div class="content">
                <p>{news.description}</p>
                <p style="text-align:center;">
                  <a href="{reverse("view_news_url", args=[news.id])}" class="button">
                    Read the full article
                  </a>
                </p>
              </div>
              <div class="footer">
                Posted on {news.created_at.strftime('%B %d, %Y')}
              </div>
            </div>
          </center>
        </body>
        </html>
        """

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=list(student_emails),
            html_message=html_message,
            fail_silently=False,
        )
        AdminAction.objects.create(
            admin=request.user,
            action=f"Added News ({news.header})"
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











