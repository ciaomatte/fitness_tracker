from django.urls import path
from .views import (
    SignUpView,
    personal_sheet,
    search_users,
    toggle_friend,
    toggle_coach,
    manage_goals,
    set_goals,
    my_goals
)

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('scheda/', personal_sheet, name='personal_sheet'),
    path('cerca/', search_users, name='search_users'),
    path('toggle_friend/<int:user_id>/', toggle_friend, name='toggle_friend'),
    path('toggle_coach/<int:user_id>/', toggle_coach, name='toggle_coach'),

    # Solo visibile ai coach: elenco atleti
    path('obiettivi/', manage_goals, name='manage_goals'),

    # Imposta obiettivi per un atleta
    path('obiettivi/<int:user_id>/', set_goals, name='set_goals'),
    path('i-tuoi-obiettivi/', my_goals, name='my_goals'),
]
