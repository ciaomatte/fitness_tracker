from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class CustomUser(AbstractUser):
    is_coach = models.BooleanField(default=False)
    friends = models.ManyToManyField('self', symmetrical=False, blank=True)

    # Nuovi campi per scheda personale
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)

    @property
    def bmi(self):
        if self.height_cm and self.weight_kg:
            return round(self.weight_kg / (self.height_cm / 100) ** 2, 2)
        return None
# users/models.py
class Goal(models.Model):
    coach = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='coached_goals')
    athlete = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='goals')
    
    target_weight = models.FloatField(null=True, blank=True)
    target_running_minutes = models.PositiveIntegerField(null=True, blank=True)
    target_swimming_minutes = models.PositiveIntegerField(null=True, blank=True)
    target_cycling_minutes = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Obiettivi di {self.athlete.username} a cura di {self.coach.username}"
