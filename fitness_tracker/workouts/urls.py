from django.urls import path
from .views import (
    feed_view,
    create_workout,
    my_workouts,
    edit_workout,
    delete_workout,
    set_goals
)

urlpatterns = [
    path('feed/', feed_view, name='feed'),
    path('workouts/new/', create_workout, name='create_workout'),
    path('workouts/miei/', my_workouts, name='my_workouts'),
    path('workouts/<int:workout_id>/edit/', edit_workout, name='edit_workout'),
    path('workouts/<int:pk>/delete/', delete_workout, name='delete_workout'),
    path('obiettivi/<int:user_id>/', set_goals, name='set_goals'),
]
