from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import FileResponse
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.conf import settings
from django.http import Http404
from a_message.models import Message
from django.db.models import Q
from .models import AdminAction, News
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from common.models import (
    UserProfile,
    CustomUser,
    ClassRoom,
    Class,
    Material,
    ActivityCategory,
)
from decimal import Decimal
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

    genders = {}
    classes_json = {}

    if classrooms.exists():
        for classroom in classrooms:
            if not classroom.class_name:
                continue
            class_students = classroom.students.all()
            genders[str(classroom.class_name)] = {
                "male": class_students.filter(user__gender="male").count(),
                "female": class_students.filter(user__gender="female").count(),
            }

        classes_json = {
            "classes": [str(c.class_name) for c in classrooms if c.class_name],
            "data": [
                {
                    "class": str(c.class_name),
                    "male": genders.get(str(c.class_name), {}).get("male", 0),
                    "female": genders.get(str(c.class_name), {}).get("female", 0),
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
        "gender_json": json.dumps(genders),
        "class_json": json.dumps(classes_json),
        "datas": data,
    }

    context.update(identify)
    return render(request, "a_school_admin/dashboard.html", context)


# =================== Material View =================


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def share_material(request):
    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        file = request.FILES.get("file")

        if not (title and file):
            messages.error(request, "Title and file are required.")
            return render(request, "a_school_admin/share-material.html", identify)

        user_profile = UserProfile.objects.get(user=request.user)
        material = Material.objects.create(
            title=title, file=file, uploaded_by=user_profile, description=description
        )
        AdminAction.objects.create(
            admin=request.user, action=f"Created Material ({material.title})"
        )
        messages.success(request, "Material created successfully.")
        return redirect("materials_list_url")

    return render(request, "a_school_admin/share-material.html", identify)


@user_passes_test(lambda user: user.is_authenticated)
def materials_list(request):
    user_profile = UserProfile.objects.get(user=request.user)
    materials = Material.objects.filter(uploaded_by=user_profile).order_by(
        "-uploaded_at"
    )

    context = {
        "materials": materials,
        "is_admin": True if request.user.role == "admin" else False,
        "is_teacher": True if request.user.role == "teacher" else False,
        "is_student": True if request.user.role == "student" else False,
    }
    return render(request, "a_school_admin/material-list.html", context)


@user_passes_test(lambda user: user.is_authenticated)
def download_material(request, material_id):
    material = get_object_or_404(Material, pk=material_id)
    response = FileResponse(
        open(material.file.path, "rb"), content_type="application/octet-stream"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{material.file.name.split("/")[-1]}"'
    )
    return response


@user_passes_test(
    lambda user: user.is_authenticated
    and user.role == "admin"
    or user.role == "teacher"
)
def edit_material(request, material_id):
    material = get_object_or_404(Material, pk=material_id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        file = request.FILES.get("file")
        has_changes = False

        if description and description != material.description:
            material.description = description
            has_changes = True

        if title and title != material.title:
            material.title = title
            has_changes = True
        if file:
            material.file = file
            has_changes = True

        if has_changes:
            material.save()
            AdminAction.objects.create(
                admin=request.user, action=f"Updated Material ({material.title})"
            )
            messages.success(request, "Material updated successfully.")
        else:
            messages.info(request, "No changes detected.")

        return redirect("materials_list_url")

    context = {"material": material}
    context.update(identify)
    return render(request, "a_school_admin/edit-material.html", context)


@user_passes_test(
    lambda user: user.is_authenticated
    and user.role == "admin"
    or user.role == "teacher"
)
def delete_material(request, material_id):
    material = get_object_or_404(Material, pk=material_id)
    if request.method == "POST":
        title = material.title
        material.delete()
        AdminAction.objects.create(
            admin=request.user, action=f"Deleted Material ({title})"
        )
        messages.success(request, "Material deleted successfully.")
        return redirect("materials_list_url")
    context = {"material": material}
    context.update(identify)
    return render(request, "a_school_admin/delete-material.html", context)


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


# =================== News =================


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def add_news(request):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        header = request.POST.get("header", "").strip()
        description = request.POST.get("description", "").strip()

        if not (photo and header and description):
            messages.error(request, "All fields are required.")
            return render(request, "a_school_admin/add-news.html", identify)

        news = News(photo=photo, header=header, description=description)
        news.save()

        _send_news_email(
            news,
            request,
            subject_prefix="📢 New News:",
            action_desc=f"Added News ({news.header})",
        )
        messages.success(request, "News item added successfully.")
        return redirect("all_news_url")

    return render(request, "a_school_admin/add-news.html", identify)


def _send_news_email(news, request, subject_prefix, action_desc):
    recipients = list(
        CustomUser.objects.exclude(email=request.user.email)
        .exclude(email__exact="")
        .values_list("email", flat=True)
    )
    # Log and exit if no recipients
    if not recipients:
        AdminAction.objects.create(admin=request.user, action=action_desc)
        return

    subject = f"{subject_prefix} {news.header}"
    plain_text = news.description
    detail_url = request.build_absolute_uri(reverse("news_detail", args=[news.id]))

    html_content = f"""
    <!DOCTYPE html>
    <html><head><meta charset=\"UTF-8\"><title>{news.header}</title></head>
    <body style=\"margin:0;padding:20px 0;background-color:#2DAA31;font-family:Arial,sans-serif;color:#222\">
      <center>
        <div style=\"max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden\">
          <div style=\"background:#196b21;padding:20px;text-align:center\">
            <h1 style=\"margin:0;color:#fff;font-size:32px\">{subject_prefix} {news.header}</h1>
          </div>
          <div style=\"padding:30px;color:#555;line-height:1.5\">
            {f'<img src=\"cid:newsimage\" style=\"max-width:100%;border-radius:8px\"><br><br>' if news.photo else ''}
            <p>{news.description}</p>
            <p style=\"text-align:center;margin:20px 0\">
              <a href=\"{detail_url}\"
                 style=\"display:inline-block;padding:12px 24px;background:#196b21;color:#fff;text-decoration:none;border-radius:4px\">
                Read the full article
              </a>
            </p>
          </div>
          <div style=\"font-size:12px;color:#999;text-align:center;padding:10px\">
            Posted on {news.created_at.strftime('%B %d, %Y')}
          </div>
        </div>
      </center>
    </body></html>
    """

    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text,
        from_email=settings.EMAIL_HOST_USER,
        to=recipients,
    )
    email.attach_alternative(html_content, "text/html")

    if news.photo:
        try:
            with open(news.photo.path, "rb") as img_f:
                img = MIMEImage(img_f.read())
                img.add_header("Content-ID", "<newsimage>")
                img.add_header(
                    "Content-Disposition", "inline", filename=news.photo.name
                )
                email.attach(img)
        except Exception:
            pass

    email.send(fail_silently=False)
    AdminAction.objects.create(admin=request.user, action=action_desc)


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

    context = {"news_list": news_list}
    context.update(identify)
    return render(request, "a_school_admin/admin-news.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def edit_news(request, id):
    news = get_object_or_404(News, pk=id)

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        image_file = request.FILES.get("photo")

        # Require both title and description
        if not (title and description):
            messages.error(request, "Title and description are required.")
            return render(request, "a_school_admin/edit-news.html", {"news": news})

        has_changes = False
        change_list = []

        # Check for changes
        if title != news.header:
            news.header = title
            has_changes = True
            change_list.append("header")

        if description != news.description:
            news.description = description
            has_changes = True
            change_list.append("description")

        if image_file and getattr(news, "photo", None) != image_file:
            news.photo = image_file
            has_changes = True
            change_list.append("photo")

        if not has_changes:
            messages.info(request, "No changes detected.")
            return redirect("all_news_url")

        # Save updated news
        news.save()

        # Prepare email notification
        recipients = list(
            CustomUser.objects.exclude(email=request.user.email)
            .exclude(email__exact="")
            .values_list("email", flat=True)
        )

        if recipients:
            subject = f"📝 News Updated: {news.header}"
            plain_text = news.description
            detail_url = request.build_absolute_uri(
                reverse("news_detail", args=[news.id])
            )

            html_content = f"""
            <!DOCTYPE html>
            <html><head><meta charset=\"UTF-8\"><title>{news.header}</title></head>
            <body style=\"margin:0;padding:20px 0;background-color:#2DAA31;font-family:Arial,sans-serif;color:#222\">
              <center>
                <div style=\"max-width:600px;margin:0 auto;background:#fff;border-radius:8px;overflow:hidden\">
                  <div style=\"background:#196b21;padding:20px;text-align:center\">
                    <h1 style=\"margin:0;color:#fff;font-size:32px\">📝 {news.header}</h1>
                  </div>
                  <div style=\"padding:30px;color:#555;line-height:1.5\">
                    {f'<img src=\"cid:newsimage\" style=\"max-width:100%;border-radius:8px\"><br><br>' if news.photo else ''}
                    <p>{news.description}</p>
                    <p style=\"text-align:center;margin:20px 0\">
                      <a href=\"{detail_url}\"
                         style=\"display:inline-block;padding:12px 24px;background:#196b21;color:#fff;text-decoration:none;border-radius:4px\">
                        View Updated Article
                      </a>
                    </p>
                  </div>
                  <div style=\"font-size:12px;color:#999;text-align:center;padding:10px\">
                    Posted on {news.created_at.strftime('%B %d, %Y')}
                  </div>
                </div>
              </center>
            </body></html>
            """

            email = EmailMultiAlternatives(
                subject=subject,
                body=plain_text,
                from_email=settings.EMAIL_HOST_USER,
                to=recipients,
            )
            email.attach_alternative(html_content, "text/html")

            # Inline image if present
            if news.photo:
                try:
                    with open(news.photo.path, "rb") as img_f:
                        img = MIMEImage(img_f.read())
                        img.add_header("Content-ID", "<newsimage>")
                        img.add_header(
                            "Content-Disposition", "inline", filename=news.photo.name
                        )
                        email.attach(img)
                except Exception:
                    pass

            email.send(fail_silently=False)

        # Log the admin action
        AdminAction.objects.create(
            admin=request.user,
            action=f"Updated News ({news.header}): {', '.join(change_list)}",
        )
        messages.success(request, "News item updated successfully.")
        return redirect("all_news_url")

    return render(request, "a_school_admin/edit-news.html", {"news": news})


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


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def manage_activity_weights(request):
    cats = list(ActivityCategory.objects.order_by("name"))

    if request.method == "POST":
        # Add new
        if request.POST.get("new_category_name"):
            name = request.POST["new_category_name"].strip()
            weight = request.POST["new_category_weight"].strip()
            if ActivityCategory.objects.filter(name__iexact=name).exists():
                messages.error(request, f'Category "{name}" already exists.')
            else:
                try:
                    w = Decimal(weight)
                    ActivityCategory.objects.create(name=name, weight=w)
                    messages.success(request, f'Added "{name}" ({w}%).')
                except:
                    messages.error(request, "Invalid weight.")
            return redirect("manage_activity_weights")

        # Update existing
        updated = False
        for cat in cats:
            raw = request.POST.get(f"weight_{cat.id}", "").strip()
            if raw:
                try:
                    new_w = Decimal(raw)
                    if cat.weight != new_w:
                        cat.weight = new_w
                        cat.save()
                        updated = True
                except:
                    messages.error(request, f"Invalid weight for {cat.name}.")
                    return redirect("a_school_admin:manage_activity_weights")

        messages.info(request, "Weights updated." if updated else "No changes.")
        return redirect("manage_activity_weights")

    # GET
    context = {
        "categories": cats,  # match your template
    }
    context.update(identify)
    return render(request, "a_school_admin/manage_activity_weights.html", context)


@user_passes_test(lambda user: user.is_authenticated and user.role == "admin")
def delete_category(request, category_id):
    category = get_object_or_404(ActivityCategory, id=category_id)
    category.delete()
    return redirect("manage_activity_weights")
