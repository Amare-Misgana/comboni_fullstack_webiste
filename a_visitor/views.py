from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages

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
    return render(request, "a_visitor/about.html")

def news(request):
    context = context = {
        "news_items": [
            {
                "title": "New Campus Opening",
                "description": "We are excited to announce the grand opening of our new campus in the northern region of the city. The facility is equipped with modern classrooms and sports areas...",
                "date": "April 20, 2025",
                "image_src": "images/news_campus.jpg",
                "url": "/news/new-campus-opening/"
            },
            {
                "title": "Tech Workshop 2025",
                "description": "Our annual tech workshop is back! Join industry leaders and learn about the latest advancements in AI, robotics, and more.",
                "date": "March 15, 2025",
                "image_src": "images/news_tech_workshop.jpg",
                "url": "/news/tech-workshop-2025/"
            },
            {
                "title": "Student Achievements",
                "description": "We are proud of our students who participated in the national science fair and brought home multiple awards across various categories...",
                "date": "February 10, 2025",
                "image_src": "images/news_student_awards.jpg",
                "url": "/news/student-achievements/"
            }
        ]
    }
    return render(request, "a_visitor/news.html", context)

def contact(request):
    if request.method == "POST":
        email = request.POST.get("email")
        message = request.POST.get("message")
        name = request.POST.get("name")
        phone_number = request.POST.get("phone_number")
        full_message = f"""
        Sender Name: {name}
        Sender Phone: {phone_number}
        Message: {message}
        """

        html_message = f"""
    <html>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; padding: 30px;">
        <div style="max-width: 600px; margin: auto; background: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50; margin-bottom: 20px;">📨 New Contact Message</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Phone Number:</strong> {phone_number}</p>
            <p><strong>Message:</strong></p>
            <div style="padding: 15px; background-color: #f7f9fa; border-left: 4px solid #3498db; color: #333; border-radius: 5px;">
                {message}
            </div>
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
        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact_url")

    return render(request, "a_visitor/contact.html", {
        "email": "example@gmail.com",
        "phone_number": "+251 911 963 441",
        "address": "Comboni School Hawassa",
    })

