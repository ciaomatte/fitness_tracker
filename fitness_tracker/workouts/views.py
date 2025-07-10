from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Workout
from .forms import WorkoutForm
from users.models import CustomUser, Goal  # assicurati di importare anche Goal

# ----------------- WORKOUTS -----------------

@login_required
def feed_view(request):
    """Mostra i workout degli amici."""
    friends = request.user.friends.all()
    workouts = Workout.objects.filter(user__in=friends).order_by('-date')
    return render(request, 'workouts/feed.html', {'workouts': workouts})


@login_required
def my_workouts(request):
    """Mostra i workout personali dell'utente."""
    workouts = Workout.objects.filter(user=request.user).order_by('-date')
    return render(request, 'workouts/my_workouts.html', {'workouts': workouts})


@login_required
def create_workout(request):
    """Permette all'utente di creare un nuovo workout."""
    if request.method == 'POST':
        form = WorkoutForm(request.POST)
        if form.is_valid():
            workout = form.save(commit=False)
            workout.user = request.user
            workout.save()
            messages.success(request, "Workout aggiunto con successo!")
            return redirect('my_workouts')
    else:
        form = WorkoutForm()
    return render(request, 'workouts/create_workout.html', {'form': form})


@login_required
def edit_workout(request, workout_id):
    """Permette all'utente di modificare un workout esistente."""
    workout = get_object_or_404(Workout, id=workout_id, user=request.user)
    if request.method == 'POST':
        form = WorkoutForm(request.POST, instance=workout)
        if form.is_valid():
            form.save()
            messages.success(request, "Workout aggiornato.")
            return redirect('my_workouts')
    else:
        form = WorkoutForm(instance=workout)
    return render(request, 'workouts/edit_workout.html', {'form': form})


@login_required
def delete_workout(request, pk):
    """Permette all'utente di eliminare un workout."""
    workout = get_object_or_404(Workout, id=pk, user=request.user)
    if request.method == 'POST':
        workout.delete()
        messages.success(request, "Workout eliminato.")
        return redirect('my_workouts')
    return render(request, 'workouts/confirm_delete.html', {'workout': workout})


# ----------------- COACH - SET GOALS -----------------

@login_required
def set_goals(request, user_id):
    """Permette al coach di impostare obiettivi per un atleta."""
    athlete = get_object_or_404(CustomUser, id=user_id)

    if not request.user.is_coach:
        messages.error(request, "Accesso negato. Solo i coach possono impostare obiettivi.")
        return redirect('feed')

    goal, _ = Goal.objects.get_or_create(athlete=athlete, coach=request.user)

    if request.method == 'POST':
        target_weight = request.POST.get('target_weight')
        target_minutes = request.POST.get('target_minutes')
        goal.target_weight = target_weight
        goal.target_minutes = target_minutes
        goal.save()
        messages.success(request, f"Obiettivi aggiornati per {athlete.username}.")
        return redirect('manage_goals')

    return render(request, 'users/set_goals.html', {
        'athlete': athlete,
        'goal': goal
    })
