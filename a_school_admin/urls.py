from django.urls import path
from . import views


urlpatterns = [
    path("", views.school_admin_dashboard, name="admin_dashboard_url"),

    # Student Urls

    path("students-mang/", views.students_mang, name="students_mang_url"),
    path("students-mang/edit-student/<str:student_username>/", views.edit_student, name="edit_student_url"),
    path("students-mang/student-detail/<str:student_username>/", views.student_detail, name="student_detail_url"),
    path("students-mang/add-student/", views.add_student, name="add_student_url"),

    # Teacher Urls


    path("teachers-mang/", views.teachers_mang, name="teachers_mang_url"),
    path("teachers-mang/edit-teacher/<str:teacher_username>/", views.edit_teacher, name="edit_teacher_url"),
    path("teachers-mang/teacher-detail/<str:teacher_username>/", views.teacher_detail, name="teacher_detail_url"),
    path("teachers-mang/add-teacher/", views.add_teacher, name="add_teacher_url"),

    # Class Urls


    path("class-mang/", views.class_mang, name="class_mang_url"),
    path("class-mang/class-detial/<str:class_name>/", views.class_detial, name="class_detail_url"),
    path("class-mang/edit-class/<str:class_name>", views.edit_class, name="edit_class_url" ),
    path("class-mang/add-class", views.add_class, name="add_class_url" ),
]