from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

def home(request):
    return render(request, "a_visitor/home.html")

def about(request):
    return render(request, "a_visitor/about.html")

def news(request):
    return render(request, "a_vistor/news.html")

def contact(request):
    if request.method == "POST":
        email = request.POST.get("email")
        message = request.POST.get("message")
        name = request.POST.get("name")
        phone_number = request.POST.get("phone number")
        full_message = f"""
        Sender Name: {name}
        Sender Phone: {phone_number}
        Message: {message}
        """

        html_message = f"""
        <html>
        <body style="font-family: Arial; background-color: #f9f9f9; padding: 20px;">
            <div style="background-color: white; padding: 20px; border-radius: 10px;">
                <h2 style="color: #333;">New Contact Message</h2>
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Phone Number:</strong> {phone_number}</p>
                <p><strong>Message:</strong></p>
                <p style="color: #555;">{message}</p>
            </div>
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

    return render(request, "a_visitor/contact.html")

