from django.db import models
from common.models import CustomUser
from a_teacher.models import QuickQuiz


class StudentQuizResult(models.Model):
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="quiz_results")
    quiz = models.ForeignKey(QuickQuiz, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    answered = models.BooleanField(default=False)
    answer_text = models.TextField(blank=True, null=True)
    answered_at = models.DateTimeField(auto_now=True)
