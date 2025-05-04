from django.urls import path
from . import views


urlpatterns = [
    path("asd/", views.school_admin_dashboard, name="admin_dashboard_url"),
    path("students-mang/", views.students_mang, name="students_mang_url"),
    path("teachers-mang/", views.teachers_mang, name="teachers_mang_url"),
    path("class-mang/", views.class_mang, name="class_mang_url"),
    path("students-mang/edit-students/<int:student_id>/", views.edit_students, name="edit_students_url"),
    path("students-mang/student-detail/<str:student_username>/", views.student_detail, name="student_detail_url"),
    path("", views.class_detial, name="class_detial_url"), #class-mang/class-detial/<int:class_id>/
    path("class-mang/edit-class/<int:class_id>", views.edit_class, name="edit_class_url" ),
]