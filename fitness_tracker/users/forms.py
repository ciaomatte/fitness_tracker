from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Goal

# Form di registrazione utente personalizzato
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'is_coach')

# Form per dati personali dell'utente
class PersonalDataForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'age', 'height_cm', 'weight_kg']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Cognome',
            'age': 'Età',
            'height_cm': 'Altezza (cm)',
            'weight_kg': 'Peso (kg)',
        }

# Form per la ricerca utenti
class UserSearchForm(forms.Form):
    username = forms.CharField(label="Cerca utente", max_length=150)

# Form per l'impostazione degli obiettivi da parte del coach
# forms.py
class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = [
            'target_weight',
            'target_running_minutes',
            'target_swimming_minutes',
            'target_cycling_minutes',
        ]
        labels = {
            'target_weight': 'Peso obiettivo (kg)',
            'target_running_minutes': 'Minuti corsa',
            'target_swimming_minutes': 'Minuti nuoto',
            'target_cycling_minutes': 'Minuti bicicletta',
        }
        widgets = {
            'target_weight': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'target_running_minutes': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'target_swimming_minutes': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
            'target_cycling_minutes': forms.NumberInput(attrs={'min': 0, 'class': 'form-control'}),
        }