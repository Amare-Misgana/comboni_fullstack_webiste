from django.urls import path
from . import views


urlpatterns = [
    path("", views.teacher_dashboard, name="teacher_dashboard_url"),
    path("chat/", views.chat, name="teacher_chat_url"),
    path("chat/<str:username>/", views.chatting, name="teachers_chatting_url"),
    path(
        "student-detail/<str:student_username>/",
        views.student_detail,
        name="teacher_student_detail_url",
    ),
    path("classes/", views.teacher_classes, name="teacher_classes_url"),
    path("edit-conduct/<str:username>/", views.edit_conduct, name="edit_conduct_url"),
    path("view-class/<str:class_name>/", views.view_class_teacher, name="view_class_url"),

    path(
        "class/<str:class_name>/activities/",
        views.activities_list,
        name="activities_list_url",
    ),
    path(
        "share-material/<str:class_name>/",
        views.share_material,
        name="share_material_teacher_url",
    ),
    path(
        "activity/<int:activity_id>/marks/",
        views.assign_marks,
        name="fill_marks_url",
    ),
]
