from django.urls import path
from . import views
from a_school_admin.views_f import view_class
from a_school_admin.views_f import view_student
from a_school_admin.views_f import view_teacher

 

urlpatterns = [

    # Dashboard Url

    path("", views.school_admin_dashboard, name="admin_dashboard_url"),
    path("chat/", views.chat, name="admin_chat_url"),
    path("chat/<str:username>/", views.chatting, name="admins_chatting_url"),
    path("news/", views.all_news_view, name="all_news_url"),
    path("news/view-news/<int:id>/", views.view_news, name="view_news_url"),
    path("news/add-news/", views.add_news, name="add_news_url"),
    path("news/edit-news/<int:id>/", views.edit_news, name="edit_news_url"),
    path("news/delete-news/<int:id>/", views.delete_news, name="delete_news_url"),

    # Student Urls

    path("students-mang/", view_student.students_mang, name="students_mang_url"),
    path("students-mang/edit-student/<str:student_username>/", view_student.edit_student, name="edit_student_url"),
    path("students-mang/student-detail/<str:student_username>/", view_student.student_detail, name="student_detail_url"),
    path("students-mang/add-student/", view_student.add_student, name="add_student_url"),
    path("students-mang/add-students/", view_student.add_students, name="add_students_url"),
    path("students-mang/download-students-excel", view_student.download_students_excel, name="download_students_excel_url"),
    path("students-mang/download-students-excel-template", view_student.download_student_excel_template, name="download_students_excel_template_url"),
    path("students-mang/delete-student/<str:student_username>/", view_student.delete_student, name="delete_student_url"),

    # Teacher Urls


    path("teachers-mang/", view_teacher.teachers_mang, name="teachers_mang_url"),
    path("teachers-mang/edit-teacher/<str:teacher_username>/", view_teacher.edit_teacher, name="edit_teacher_url"),
    path("teachers-mang/teacher-detail/<str:teacher_username>/", view_teacher.teacher_detail, name="teacher_detail_url"),
    path("teachers-mang/add-teacher/", view_teacher.add_teacher, name="add_teacher_url"),
    path("teachers-mang/add-teachers/", view_teacher.add_teachers, name="add_teachers_url"),
    path("teachers-mang/delete-teacher/<str:teacher_username>/", view_teacher.delete_teacher, name="delete_teacher_url"),
    path("teachers-mang/download-teachers-excel-template", view_teacher.download_teacher_excel_template, name="download_teachers_excel_template_url"),

    # Class Urls


    path("class-mang/", view_class.class_mang, name="class_mang_url"),
    path("class-mang/assign-student/<int:classroom_id>/", view_class.assign_subject_view, name="assign_subject_url"),
    path("class-mang/create-subjects/", view_class.create_subjects, name="add_subjects_url"),
    path("class-mang/subject/edit/<str:subject_name>/", view_class.edit_subject, name="edit_subject_url"),
    path("class-mang/subject/delete/<str:subject_name>/", view_class.delete_subject, name="delete_subject_url"),
    path("class-mang/class-detial/<str:class_name>/", view_class.class_detail, name="class_detail_url"),
    path("class-mang/edit-class/<str:class_name>", view_class.edit_class, name="edit_class_url" ),
    path("class-mang/create-classes", view_class.create_classes, name="create_classes_url"),
    path("class-mang/add-studens/<str:defined_class_room>/", view_class.defined_class, name="add_defined_student_url"),
]