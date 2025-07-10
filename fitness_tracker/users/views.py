from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Sum
from .models import CustomUser, Goal
from .forms import CustomUserCreationForm, PersonalDataForm, UserSearchForm, GoalForm
from workouts.models import Workout

User = get_user_model()

# -------- SIGNUP --------
class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('feed')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

# -------- SCHEDA PERSONALE --------
@login_required
def personal_sheet(request):
    user = request.user
    form = PersonalDataForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('personal_sheet')
    return render(request, 'users/personal_sheet.html', {
        'form': form,
        'bmi': user.bmi
    })

# -------- CERCA UTENTI / AMICI / COACH --------
@login_required
def search_users(request):
    form = UserSearchForm()
    result = None
    is_friend = False
    is_coach = False
    show_actions = False

    if request.method == 'POST':
        form = UserSearchForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if username == request.user.username:
                messages.info(request, "Non puoi cercare te stesso.")
            else:
                try:
                    result = User.objects.get(username=username)
                    is_friend = result in request.user.friends.all()
                    is_coach = result.is_coach
                    show_actions = True
                except User.DoesNotExist:
                    messages.warning(request, f"L'utente '{username}' non esiste.")

    return render(request, 'users/search_users.html', {
        'form': form,
        'result': result,
        'is_friend': is_friend,
        'is_coach': is_coach,
        'show_actions': show_actions,
    })

# -------- AGGIUNGI / RIMUOVI AMICO --------
@login_required
def toggle_friend(request, user_id):
    target = get_object_or_404(CustomUser, id=user_id)
    if target in request.user.friends.all():
        request.user.friends.remove(target)
        target.friends.remove(request.user)
        messages.info(request, f"Hai rimosso {target.username} dagli amici.")
    else:
        request.user.friends.add(target)
        target.friends.add(request.user)
        messages.success(request, f"Hai aggiunto {target.username} agli amici.")
    return redirect('search_users')

# -------- AGGIUNGI / RIMUOVI COACH --------
@login_required
def toggle_coach(request, user_id):
    target = get_object_or_404(User, id=user_id)

    if not target.is_coach:
        messages.error(request, f"{target.username} non è un coach e non può essere aggiunto come tale.")
        return redirect('search_users')

    # Aggiunta o rimozione del coach alla relazione personalizzata (es: `my_coaches`)
    # Se non hai relazioni m2m dedicate, puoi solo mostrare info e bloccare il toggle
    messages.success(request, f"{target.username} è già un coach e puoi seguirlo.")
    return redirect('search_users')

# -------- FEED --------
@login_required
def feed_view(request):
    friends = request.user.friends.all()
    workouts = Workout.objects.filter(user__in=friends).order_by('-date')
    return render(request, 'workouts/feed.html', {'workouts': workouts})

# -------- COACH: GESTISCI ATLETI --------
@login_required
def manage_goals(request):
    if not request.user.is_coach:
        messages.error(request, "Accesso riservato ai coach.")
        return redirect("feed")

    # Prende gli atleti a cui questo coach ha assegnato obiettivi
    athlete_ids = Goal.objects.filter(coach=request.user).values_list('athlete_id', flat=True)
    athletes = CustomUser.objects.filter(id__in=athlete_ids)

    return render(request, 'users/manage_goals.html', {
        'athletes': athletes
    })

# -------- COACH: IMPOSTA OBIETTIVI --------
@login_required
def set_goals(request, user_id):
    if not request.user.is_coach:
        messages.error(request, "Accesso negato.")
        return redirect("feed")

    athlete = get_object_or_404(CustomUser, id=user_id)
    goal, created = Goal.objects.get_or_create(coach=request.user, athlete=athlete)

    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            # ⬇️ Imposta direttamente tutti i campi, anche se valgono 0
            goal = form.save(commit=False)
            goal.coach = request.user
            goal.athlete = athlete
            goal.save()
            messages.success(request, f"Obiettivi aggiornati per {athlete.username}.")
            return redirect('manage_goals')
    else:
        form = GoalForm(instance=goal)

    return render(request, 'users/set_goals.html', {
        'athlete': athlete,
        'form': form
    })


    
# -------- ATLETA: VISUALIZZA I PROPRI OBIETTIVI --------
@login_required
def my_goals(request):
    user = request.user
    goal = Goal.objects.filter(athlete=user).first()
    coach = goal.coach if goal else None

    workouts = Workout.objects.filter(user=user)
    run_minutes = workouts.filter(type='run').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
    swim_minutes = workouts.filter(type='swim').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0
    bike_minutes = workouts.filter(type='bike').aggregate(Sum('duration_minutes'))['duration_minutes__sum'] or 0

    def status(current, target):
        if target is None:
            return "—"
        return "✅ Completato" if current >= target else "⏳ In corso"

    activity_goals = []

    if goal:
        # NON usare `if goal.target_XYZ_minutes` perché salta se è 0!
        for label, value, current in [
            ('🏃‍♂️ Corsa', goal.target_running_minutes, run_minutes),
            ('🏊‍♂️ Nuoto', goal.target_swimming_minutes, swim_minutes),
            ('🚴‍♂️ Bici', goal.target_cycling_minutes, bike_minutes),
        ]:
            if value is not None:
                activity_goals.append({
                    'label': label,
                    'current': current,
                    'target': value,
                    'status': status(current, value),
                })

    weight_status = None
    if goal and goal.target_weight is not None and user.weight_kg:
        weight_status = "✅ Completato" if user.weight_kg <= goal.target_weight else "⏳ In corso"

    return render(request, 'users/my_goals.html', {
        'coach': coach,
        'goal': goal,
        'activity_goals': activity_goals,
        'target_weight': goal.target_weight if goal else None,
        'current_weight': user.weight_kg,
        'weight_status': weight_status,
    })
