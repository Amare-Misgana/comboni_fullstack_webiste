from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test


@user_passes_test(lambda user: user.is_authenticated and user.role=="teacher")
def teacher_dashboard(request):
    return render(request, "a_teacher/dashboard.html")
