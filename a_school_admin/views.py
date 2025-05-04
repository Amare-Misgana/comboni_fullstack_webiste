from django.shortcuts import render, redirect, get_object_or_404
from common.models import UserProfile, CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib import messages


@login_required
def school_admin_dashboard(request):
    # user = UserProfile.objects.get(user=request.user)
    names = list(CustomUser.objects.values_list('first_name', flat=True))
    context = {
        # "user_pic_url8": user.user_pic.url,
        # "username8": user.username,
        "names": names,
    }
    return render(request, "a_school_admin/dashboard.html", context)

@login_required
def edit_students(request, student_id):
    Student = get_user_model()
    student = Student.objects.get(id=student_id)
    StudentProfile = get_object_or_404(UserProfile, user=student)

    if request.method == 'POST':
        student.first_name = request.POST.get('first_name')
        student.middle_name = request.POST.get('middle_name', '')
        student.last_name = request.POST.get('last_name')
        student.phone_number = request.POST.get('phone_number')
        student.email = request.POST.get('email')


        password = request.POST.get('password')
        if password:
            student.password = make_password(password)
            StudentProfile.password = password

        profile_image = request.FILES.get('profile_image')
        if profile_image:
            StudentProfile.user_pic = profile_image

        student.save()
        messages.success(request, 'Student updated successfully.')
        return redirect('students_mang_url')
    return render(request, "a_school_admin/edit-students.html")

@login_required
def add_student(request):
    return render(request, "a_school_admin/add-student.html")

@login_required
def edit_class(request, class_id):
    return render(request, "a_school_admin/edit-class.html")

@login_required
def class_detial(request): #, class_id
    return render(request, "a_school_admin/class-detail.html")



@login_required
def student_detail(request, student_username):
    Student = get_user_model()
    student = Student.objects.get(username=student_username)
    student_profile = get_object_or_404(UserProfile, user=student)
    context = {
        "student": student,
        "student_profile": student_profile,
    }
    return render(request, "a_school_admin/student-detail.html", context)



@login_required
def students_mang(request):
    User = get_user_model()
    students = User.objects.filter(role='student')
    context = {
        "students": students,
    }
    return render(request, "a_school_admin/students-mang.html", context)

@login_required
def teachers_mang(request):
    return render(request, "a_school_admin/teachers-mang.html")

@login_required
def class_mang(request):
    return render(request, "a_school_admin/class-mang.html")

@login_required
def user_search(request):
    names = list(CustomUser.objects.values_list('first_name', flat=True))
    return render(request, 'a_school_admin/example.html', {'names': names})

@login_required
def materials(request):
    pass