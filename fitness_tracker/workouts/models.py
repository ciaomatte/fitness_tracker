from django.db import models
from users.models import CustomUser

class Workout(models.Model):
    WORKOUT_CHOICES = [
        ('run', 'Corsa'),
        ('swim', 'Nuoto'),
        ('bike', 'Bicicletta'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=WORKOUT_CHOICES)
    duration_minutes = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_type_display()} ({self.duration_minutes} min)"
