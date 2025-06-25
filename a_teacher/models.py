from django.db import models
from common.models import CustomUser


class TeacherAction(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name="teacher")
    action = models.CharField(max_length=300)
    timestamp = models.DateTimeField(auto_now_add=True)


class QuickQuiz(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="quizzes")

    TYPE_TF = "TF"
    TYPE_MC = "MC"
    TYPE_FILL = "FI"
    TYPE_CHOICES = [
        (TYPE_TF, "True / False"),
        (TYPE_MC, "Multiple choice"),
        (TYPE_FILL, "Fill in the blank"),
    ]

    quiz_name = models.CharField(max_length=150)
    type = models.CharField(max_length=2, choices=TYPE_CHOICES)
    paragraph = models.TextField()
    explanation = models.TextField(help_text="Shown if wrong")
    correct_answer = models.CharField("Answer (fill)", max_length=200, blank=True)
    is_correct = models.BooleanField(default=False)
    answered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quiz_name} ({self.get_type_display()})"


class QuizChoice(models.Model):
    quiz = models.ForeignKey(QuickQuiz, on_delete=models.CASCADE, related_name="choices")
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text
