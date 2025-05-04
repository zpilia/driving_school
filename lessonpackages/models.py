from django.db import models
from django.conf import settings

class LessonPackage(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_packages"
    )
    total_hours = models.FloatField(default=0)
    used_hours = models.FloatField(default=0)
    paid_hours = models.FloatField(default=0)
    unpaid_hours = models.FloatField(default=0)

    def __str__(self):
        return f"{self.student.username} - {self.total_hours}h totales, {self.used_hours}h utilisées"

    def remaining_hours(self):
        return self.total_hours - self.used_hours

    def save(self, *args, **kwargs):
        self.total_hours = self.paid_hours + self.unpaid_hours
        super().save(*args, **kwargs)

