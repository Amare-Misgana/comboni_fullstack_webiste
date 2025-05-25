from django.urls import path
from . import views


urlpatterns = [
    path("", views.teacher_dashboard, name="teacher_dashboard_url"),
    path("chat/", views.chat, name="teacher_chat_url"),
    path("chat/<str:username>/", views.chatting, name="teachers_chatting_url"),
]