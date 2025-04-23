from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings

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
    })

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

