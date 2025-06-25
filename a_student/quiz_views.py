from django.shortcuts import render, get_object_or_404
from a_teacher.models import QuickQuiz, CustomUser
from .models import StudentQuizResult
from django.db.models import Count, Q

identify = {
    "is_student": True,
    "is_teacher": False,
    "is_admin": False,
}


from django.db.models import Count


def student_quiz_view(request):
    # Get quizzes grouped by teacher and quiz_name with count of questions
    quizzes = (
        QuickQuiz.objects.values("teacher", "quiz_name")
        .annotate(total_questions=Count("id"))
        .order_by("teacher", "quiz_name")
    )

    # Get teacher objects for all teachers involved
    teacher_ids = {q["teacher"] for q in quizzes}
    teachers = {t.id: t for t in CustomUser.objects.filter(id__in=teacher_ids)}

    # Attach teacher object to each quiz grouping
    for quiz in quizzes:
        quiz["teacher_obj"] = teachers.get(quiz["teacher"])

    context = {"quizzes": quizzes, **identify}
    return render(request, "a_student/quiz.html", context)


def student_quiz_detail(request, teacher_id, quiz_name):
    student = request.user
    teacher = get_object_or_404(CustomUser, id=teacher_id)
    questions = QuickQuiz.objects.filter(teacher=teacher, quiz_name=quiz_name)

    if request.method == "POST":
        question_id = request.POST.get("question_id")
        answer = request.POST.get("answer")
        question = get_object_or_404(QuickQuiz, id=question_id)

        # Create/update student result
        result, created = StudentQuizResult.objects.get_or_create(
            student=student, quiz=question, defaults={"answered": True, "is_correct": False, "answer_text": answer}
        )
        if not created:
            result.answered = True
            result.answer_text = answer

        # Check correctness
        correct_answer = question.correct_answer.lower().strip()
        result.is_correct = answer.lower().strip() == correct_answer
        result.save()

    # Get results and prepare context
    student_results = StudentQuizResult.objects.filter(student=student, quiz__in=questions)
    results_dict = {r.quiz.id: r for r in student_results}

    question_results = []
    for q in questions:
        result = results_dict.get(q.id)
        question_results.append((q, result))

    total = questions.count()
    correct = sum(1 for r in student_results if r.is_correct)

    context = {
        "question_results": question_results,
        "teacher": teacher,
        "quiz_name": quiz_name,
        "total": total,
        "correct": correct,
        **identify,
    }
    return render(request, "a_student/quiz_detail.html", context)
