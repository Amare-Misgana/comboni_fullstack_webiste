from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout,  login, get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from a_school_admin.models import News

def home(request):
    testimonial = [
        {
            "src": "a_visitor/images/yosi.jpg",
            "alt": "Message by Yosph Mulugeta from 11C",
            "message": "CSSS is more than a school — it’s a family. I’ve grown academically and personally thanks to the amazing staff and programs.",
            "message_by": "Yosph Mulugeta, 11C"
        },
        {
            "src": "a_visitor/images/sami.webp",
            "alt": "Message by Samrawit Getachew from 10A",
            "message": "The support I get from my teachers at CSSS is unmatched. They truly care about our success.",
            "message_by": "Samrawit Getachew, 10A"
        },
        {
            "src": "a_visitor/images/miki.jfif",
            "alt": "Message by Mikias Tadesse from 9B",
            "message": "I’ve made lifelong friends at Comboni and discovered a love for science and innovation.",
            "message_by": "Mikias Tadesse, 9B"
        },
        {
            "src": "a_visitor/images/blen.jpg",
            "alt": "Message by Blen Yared from 12D",
            "message": "CSSS pushes me to aim higher and be my best self every day. I’m proud to be here.",
            "message_by": "Blen Yared, 12D"
        },
        {
            "src": "a_visitor/images/caleb.jpg",
            "alt": "Message by Caleb Daniel from 11A",
            "message": "From leadership skills to academic excellence, CSSS has given me so much to be thankful for.",
            "message_by": "Caleb Daniel, 11A"
        }
    ]

        

    return render(request, "a_visitor/home.html", {
        "email": "example@gmail.com",
        "phone_number": "+251 911 963 441",
        "address": "Comboni School Hawassa",
        "testimonial": testimonial,
        "is_cta": True,
    })

def about(request):
    return render(request, "a_visitor/about.html", {
         "email": "example@gmail.com",
        "phone_number": "+251 911 963 441",
        "address": "Comboni School Hawassa",
    })

def news(request):
    cutoff = timezone.now() - timedelta(days=7)

    # querysets
    recent_qs = News.objects.filter(created_at__gte=cutoff).order_by('-created_at')
    older_qs  = News.objects.filter(created_at__lt=cutoff).order_by('-created_at')

    # helper to map model → dict
    def to_dict(n):
        return {
            "title":       n.header,
            "description": n.description,
            "date":        n.created_at.strftime("%B %d, %Y"),
            "image_src":   n.photo.url,
            "url":         reverse('news_detail', args=[n.pk]),
        }

    context = {
        "recent_news":      [to_dict(n) for n in recent_qs],
        "news_other_items": [to_dict(n) for n in older_qs],
        "email":            "example@gmail.com",
        "phone_number":     "+251 911 963 441",
        "address":          "Comboni School Hawassa",
    }
    return render(request, "a_visitor/news.html", context)

def news_detail(request, pk):
    item = get_object_or_404(News, pk=pk)
    context = {
        "title": item.header,
        "description": item.description,
        "date": item.created_at.strftime("%B %d, %Y"),
        "image_src": item.photo.url,
    }
    return render(request, "a_visitor/news_detail.html", context)


def contact(request):
    if request.method == "POST":
        email = request.POST.get("email")
        message = request.POST.get("message")
        name = request.POST.get("name")
        phone_number = request.POST.get("phone_number")

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Invalid email.")
            return render(request, 'a_visitor/contact.html')

        full_message = f"""
        Sender Name: {name}
        Sender Phone: {phone_number}
        Message: {message}
        """

        html_message = f"""
    <!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin:0;padding:20px 0;background-color:#0d8817;font-family:Arial, Helvetica, sans-serif;">
    <center>
        <!--[if mso]>
        <table cellpadding="0" cellspacing="0" border="0" style="padding:20px 0;">
        <tr>
        <td>
        <![endif]-->
        
        <div style="max-width:600px;margin:0 auto;">
            <h1 style="margin:0 0 20px 0;color:#ffffff;text-align:center;font-size:32px;">📨 Contact Info</h1>
            
            <div style="background-color:#ffffff;padding:30px;border-radius:4px;">
                <table cellpadding="0" cellspacing="0" style="width:100%;">
                    <tr>
                        <td style="padding-bottom:15px;">
                            <h3 style="margin:0;font-size:18px;"><strong>Name:</strong> {name}</h3>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding-bottom:15px;">
                            <h3 style="margin:0;font-size:18px;"><strong>Email:</strong> {email}</h3>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding-bottom:15px;">
                            <h3 style="margin:0;font-size:18px;">
                                <strong>Phone Number:</strong>
                                <a href="tel:{phone_number}" style="color:#000000;text-decoration:none;">{phone_number}</a>
                            </h3>
                        </td>
                    </tr>
                    <tr>
                        <td>
                            <h3 style="margin:0 0 10px 0;font-size:18px;"><strong>Message:</strong></h3>
                            <div style="background-color:#b1f7ae;padding:15px;border-left:4px solid #0d8817;">
                                {message}
                            </div>
                        </td>
                    </tr>
                </table>
            </div>
        </div>

        <!--[if mso]>
        </td>
        </tr>
        </table>
        <![endif]-->
    </center>
</body>
</html>
    """

        send_mail(
            subject="Contact Us Message",
            message=full_message,
            from_email=email,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
            html_message=html_message
        )
        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact_url")

    context = {
        "email": "example@gmail.com",
        "phone_number": "+251 911 963 441",
        "address": "Comboni School Hawassa",
    }

    return render(request, "a_visitor/contact.html", context)


def login_choice(request):
    context = {
        "email": "example@gmail.com",
        "phone_number": "+251 911 963 441",
        "address": "Comboni School Hawassa",
    }
    return render(request, "a_visitor/login_choice.html", context)


def login_view(request, role):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        UserModel = get_user_model()

        try:
            user = UserModel.objects.get(email=email)
            if not user.check_password(password):
                messages.error(request, "Incorrect password.")
                return redirect(reverse('login_url', kwargs={'role': role}))

            if user.role != role:
                messages.error(request, f"Wrong portal. You are not registered in {role}.")
                return redirect(reverse('login_url', kwargs={'role': role}))
        except UserModel.DoesNotExist:
            messages.error(request, "Email does not exist.")
            return redirect(reverse('login_url', kwargs={'role': role}))

        login(request, user)
        messages.success(request, "Logged in successfully.")
        return redirect(f"{role}_dashboard_url")

    context = {
        "email": "example@gmail.com",
        "phone_number": "+251 911 963 441",
        "address": "Comboni School Hawassa",
        "title_sub": f"Login As {role}",
    }
    return render(request, "a_visitor/login.html", context)

def logout_view(request):
    messages.success(request, "You have been successfully logged out. See you next time!")
    logout(request)
    return redirect("home_url")