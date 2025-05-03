from django.db import models
from django.conf import settings

class TrainingProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="training_progresses",
        verbose_name="Élève"
    )
    total_lessons = models.PositiveIntegerField(
        default=0,
        help_text="Nombre total de leçons dans le programme",
        verbose_name="Nombre total de leçons"
    )
    completed_lessons = models.PositiveIntegerField(
        default=0,
        help_text="Nombre de leçons déjà complétées par l’élève",
        verbose_name="Leçons complétées"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Mis à jour le"
    )

    def progress_percentage(self):
        if self.total_lessons:
            return (self.completed_lessons / self.total_lessons) * 100
        return 0

    def __str__(self):
        return f"{self.student.username} : {self.progress_percentage():.1f}% complété"
