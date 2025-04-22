from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home_url"),
    path("contact/", views.contact, name="contact_url"),
    path("about/", views.about, name="about_url"),
    path("news/", views.news, name="news_url"),
]