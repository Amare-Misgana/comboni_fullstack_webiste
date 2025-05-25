from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home_url"),
    path("contact/", views.contact, name="contact_url"),
    path("about/", views.about, name="about_url"),
    path("news/", views.news, name="news_url"),
    path("news/<int:pk>", views.news_detail, name="news_detail"),
    path("login-choice/", views.login_choice, name="login_choice_url"),
    path("login/<str:role>/", views.login_view, name="login_url"),
    path("logout/", views.logout_view, name="logout_url"),
]