from django.shortcuts import render

def home(request):
    return render(request, "a_visiter/home/html")

def contact(request):
    return render(request, "a_visiter/contact.html")
