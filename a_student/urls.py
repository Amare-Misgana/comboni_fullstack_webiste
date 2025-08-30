from django.urls import path
from . import views
from . import quiz_views

urlpatterns = [
    path("quizzes/", quiz_views.student_quiz_view, name="student_quiz_view"),
    path("quizzes/<int:teacher_id>/<str:quiz_name>/", quiz_views.student_quiz_detail, name="student_quiz_detail"),
    path("", views.student_dashboard, name="student_dashboard_url"),
    path("chat/", views.chat, name="student_chat_url"),
    path("chat/<str:username>/", views.chatting, name="students_chatting_url"),
    path("material/", views.material, name="student_material"),
]
