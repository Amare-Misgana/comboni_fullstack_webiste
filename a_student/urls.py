from django.urls import path
from . import views


urlpatterns = [
    path("", views.student_dashboard, name="student_dashboard_url"),
    path("chat/", views.chat, name="student_chat_url"),
    path("chat/<str:username>/", views.chatting, name="students_chatting_url"),
    path("material/", views.material, name="student_material"),
]