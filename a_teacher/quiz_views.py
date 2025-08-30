from django.shortcuts import render, redirect
from .models import QuickQuiz, QuizChoice, CustomUser

identify = {
    "is_student": False,
    "is_teacher": True,
    "is_admin": False,
}


def quiz_create(request):
    if request.method == "POST":
        q = QuickQuiz.objects.create(
            teacher=request.user,
            quiz_name=request.POST["quiz_name"],
            type=request.POST["type"],
            paragraph=request.POST["paragraph"],
            explanation=request.POST["explanation"],
            correct_answer=request.POST.get("correct_answer", ""),
        )

        if q.type in (QuickQuiz.TYPE_TF, QuickQuiz.TYPE_MC):

            n = 2 if q.type == QuickQuiz.TYPE_TF else 4
            for i in range(1, n + 1):
                text = request.POST[f"choice{i}"]
                correct = request.POST.get("correct") == f"choice{i}"
                QuizChoice.objects.create(quiz=q, text=text, is_correct=correct)

    return render(request, "a_teacher/quiz.html", identify)
