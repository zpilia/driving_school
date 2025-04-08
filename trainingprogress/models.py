from django.db import models
from django.conf import settings

class TrainingProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="training_progresses"
    )
    total_lessons = models.PositiveIntegerField(default=0, help_text="Total number of lessons in the program")
    completed_lessons = models.PositiveIntegerField(default=0, help_text="Number of lessons completed by the student")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def progress_percentage(self):
        if self.total_lessons:
            return (self.completed_lessons / self.total_lessons) * 100
        return 0

    def __str__(self):
        return f"{self.student.username}: {self.progress_percentage():.1f}% completed"
