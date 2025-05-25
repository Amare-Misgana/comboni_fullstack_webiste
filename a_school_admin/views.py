from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import Http404
from a_message.models import Message
from django.db.models import Q
from .models import AdminAction, News
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
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
    classes = sorted(
        set(
            int(item[:-1])
            for item in Class.objects.values_list("class_name", flat=True)
        )
    )

    classrooms = ClassRoom.objects.select_related(
        "class_name", "room_teacher"
    ).prefetch_related("students")

    grades = {}
    for classroom in classrooms:
        if not classroom.class_name:
            continue
        class_students = classroom.students.all()
        grades[str(classroom.class_name)] = {
            "male": class_students.filter(user__gender="male").count(),
            "female": class_students.filter(user__gender="female").count(),
        }

    classes_json = {
        "classes": [str(c.class_name) for c in classrooms if c.class_name],
        "data": [
            {
                "class": str(c.class_name),
                "male": grades.get(str(c.class_name), {}).get("male", 0),
                "female": grades.get(str(c.class_name), {}).get("female", 0),
            }
            for c in classrooms
            if c.class_name
        ],
    }

    admin_actions = (
        AdminAction.objects.select_related("admin").all().order_by("-timestamp")
    )
    admin_profiles = UserProfile.objects.select_related("user").all()

    action_profiles = []
    for action in admin_actions:
        profile = next((p for p in admin_profiles if p.user == action.admin), None)
        if profile:
            action_profiles.append((action, profile))

    data = [
        {"data": request.user.phone_number, "name": "Phone Number"},
        {"data": request.user.email, "name": "Email"},
    ]

    context = {
        "user_profile": user_profile,
        "students_amount": students.count(),
        "teachers_amount": teachers.count(),
        "classes_amount": len(classes),
        "sections_amount": classrooms.count(),
        "class": sorted(
            {c.class_name.class_name[:-1] for c in classrooms if c.class_name}
        ),
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


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def chat(request):
    me = UserProfile.objects.get(user=request.user)
    teachers = UserProfile.objects.filter(user__role="teacher")
    admins = UserProfile.objects.filter(user__role="admin").exclude(pk=me.pk)

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
        "teachers": attach_last_msg(teachers),
        "admins": attach_last_msg(admins),
    }
    context.update(identify)
    return render(request, "fragments/chat.html", context)


def get_room_name(user1, user2):
    users = sorted([str(user1).lower(), str(user2).lower()])
    return f"chat_{users[0]}-{users[1]}"


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def chatting(request, username):
    me = UserProfile.objects.get(user=request.user)
    students = UserProfile.objects.filter(user__role="student")
    teachers = UserProfile.objects.filter(user__role="teacher")
    admins = UserProfile.objects.filter(user__role="admin").exclude(id=me.id)

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
    }
    context.update(identify)
    return render(request, "fragments/chatting.html", context)


from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from .models import News, AdminAction, CustomUser


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_news(request):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        header = request.POST.get("header", "").strip()
        description = request.POST.get("description", "").strip()

        if not (photo and header and description):
            messages.error(request, "All fields are required.")
            return render(request, "a_school_admin/add-news.html")

        news = News(photo=photo, header=header, description=description)
        news.save()

        student_emails = CustomUser.objects.filter(role="student").values_list(
            "email", flat=True
        )

        subject = f"📢 New News: {news.header}"
        plain_message = news.description

        html_message = f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <title>{news.header}</title>
        </head>
        <body style="margin:0; padding:20px 0; background-color:rgb(45, 170, 49); font-family:Arial, Helvetica, sans-serif; color:#222;">
          <center>
            <div style="max-width:600px; margin:0 auto; background:#fff; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1); overflow:hidden;">
              <div style="background:#196b21; padding:20px; text-align:center;">
                <h1 style="margin:0; color:#fff; font-size:32px;">📢 {news.header}</h1>
              </div>
              <div style="padding:30px; color:#555; line-height:1.5;">
                <img src="cid:newsimage" alt="News Image" style="max-width:100%; height:auto; border-radius:8px;"><br><br>
                <p>{news.description}</p>
                <p style="text-align:center; margin:20px 0;">
                  <a href="{request.build_absolute_uri(reverse('news_detail', args=[news.id]))}"
                     style="display:inline-block; padding:12px 24px; background:#196b21; color:#fff !important;
                            text-decoration:none; border-radius:4px;">
                    Read the full article
                  </a>
                </p>
              </div>
              <div style="font-size:12px; color:#999; text-align:center; padding:10px;">
                Posted on {news.created_at.strftime('%B %d, %Y')}
              </div>
            </div>
          </center>
        </body>
        </html>
        """

        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.EMAIL_HOST_USER,
            to=list(student_emails),
        )
        email.attach_alternative(html_message, "text/html")

        try:
            with open(news.photo.path, "rb") as img_file:
                img = MIMEImage(img_file.read())
                img.add_header("Content-ID", "<newsimage>")
                img.add_header("Content-Disposition", "inline", filename=photo.name)
                email.attach(img)
        except Exception as e:
            print("Image attach failed:", e)

        email.send(fail_silently=False)

        AdminAction.objects.create(
            admin=request.user, action=f"Added News ({news.header})"
        )
        messages.success(request, "News item added!")

    return render(request, "a_school_admin/add-news.html", identify)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def all_news_view(request):
    news_qs = News.objects.all().order_by("-created_at")
    news_list = []

    for item in news_qs:
        news_list.append(
            {
                "id": item.id,
                "title": item.header,
                "description": item.description,
                "image_src": item.photo.url,
                "date": item.created_at.strftime("%B %d, %Y"),
                "url": f"/news/{item.id}/",
            }
        )

    context = {"news_list": news_list, "is_admin": True}
    return render(request, "a_school_admin/admin-news.html", context)


from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from .models import News, AdminAction, CustomUser


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_news(request, id):
    try:
        news = News.objects.get(id=id)
    except News.DoesNotExist:
        messages.error(request, "Can't find the news.")
        return redirect("all_news_url")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        image_file = request.FILES.get("photo")

        if title and description:
            news.header = title
            news.description = description
            if image_file:
                news.photo = image_file
            news.save()

            emails = CustomUser.objects.exclude(email=request.user.email).values_list(
                "email", flat=True
            )

            subject = f"📝 News Updated: {news.header}"
            plain_text = news.description

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head><meta charset="UTF-8"><title>{news.header}</title></head>
            <body style="margin:0; padding:20px 0; background-color:rgb(45, 170, 49); font-family:Arial, Helvetica, sans-serif; color:#222;">
              <center>
                <div style="max-width:600px; margin:0 auto; background:#fff; border-radius:8px; box-shadow:0 2px 4px rgba(0,0,0,0.1); overflow:hidden;">

                  <div style="background:#196b21; padding:20px; text-align:center;">
                    <h1 style="margin:0; color:#fff; font-size:32px;">
                      📝 {news.header}
                    </h1>
                  </div>

                  <div style="padding:30px; color:#555; line-height:1.5;">
                    <img src="cid:newsimage" alt="News Image" style="max-width:100%; height:auto; border-radius:8px;"><br><br>
                    <p>{news.description}</p>
                    <p style="text-align:center; margin:20px 0;">
                      <a href="{request.build_absolute_uri(reverse('news_detail', args=[news.id]))}"
                         style="display:inline-block; padding:12px 24px; background:#196b21; color:#fff !important;
                                text-decoration:none; border-radius:4px;">
                        View Updated Article
                      </a>
                    </p>
                  </div>

                  <div style="font-size:12px; color:#999; text-align:center; padding:10px;">
                    Posted on {news.created_at.strftime('%B %d, %Y')}
                  </div>

                </div>
              </center>
            </body>
            </html>
            """

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_text,
                from_email=settings.EMAIL_HOST_USER,
                to=list(emails),
            )
            email.attach_alternative(html_content, "text/html")
            try:
                with open(news.photo.path, "rb") as img_f:
                    img = MIMEImage(img_f.read())
                    img.add_header("Content-ID", "<newsimage>")
                    img.add_header(
                        "Content-Disposition", "inline", filename=news.photo.name
                    )
                    email.attach(img)
            except Exception as e:
                print("Failed to attach image:", e)

            email.send(fail_silently=False)

            AdminAction.objects.create(
                admin=request.user, action=f"Updated News ({news.header})"
            )
            messages.success(request, "News item updated and emailed!")

            return redirect("all_news_url")

    context = {"news": news}
    context.update(identify)
    return render(request, "a_school_admin/edit-news.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def delete_news(request, id):
    news = get_object_or_404(News, pk=id)
    if request.method == "POST":
        news.delete()
        messages.success(request, "Successfully deleted the message.")
        return redirect("all_news_url")
    context = {"news": news}
    context.update(identify)
    return render(request, "a_school_admin/delete-news.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def view_news(request, id):
    news = get_object_or_404(News, pk=id)
    context = {"news": news}
    context.update(identify)
    return render(request, "a_school_admin/view-news.html", context)
