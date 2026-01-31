from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Card, Duel, Prompt
from .forms import ImageCardForm, PromptCardForm
import random
from django.db.models import Count
from .utils import update_elo

def index(request):
    error = None
    if request.method == 'POST':
        password = request.POST.get('password')
        try:
            profile = Profile.objects.get(password=password)
            request.session['profile_id'] = profile.id
            return redirect('profile_home', profile_id=profile.id)
        except Profile.DoesNotExist:
            error = "Invalid password. Please try again."
            
    return render(request, 'index.html', {'error': error})

def profile_home(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    # Simple security check
    if request.session.get('profile_id') != profile.id:
         return redirect('index') # Redirect to index instead of profile_login since it's gone
    
    return render(request, 'profile_home.html', {'profile': profile})

def upload_image_card(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    if request.method == 'POST':
        form = ImageCardForm(request.POST, request.FILES)
        if form.is_valid():
            card = form.save(commit=False)
            card.profile = profile
            card.submitted_by = "User" # We might want to capture a name later, but for now generic.
            card.save()
            return redirect('profile_home', profile_id=profile.id)
    else:
        form = ImageCardForm()
    
    return render(request, 'upload_card.html', {'form': form, 'profile': profile, 'title': 'Upload Photo Card'})

def upload_prompt_card(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    if request.method == 'POST':
        form = PromptCardForm(request.POST, request.FILES)
        if form.is_valid():
            card = form.save(commit=False)
            card.profile = profile
            card.submitted_by = "User"
            card.save()
            return redirect('profile_home', profile_id=profile.id)
    else:
        form = PromptCardForm()
    
    return render(request, 'upload_card.html', {'form': form, 'profile': profile, 'title': 'Answer a Prompt'})

def rank_cards(request, profile_id, card_type):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    if request.method == 'POST':
        winner_id = request.POST.get('winner')
        loser_id = request.POST.get('loser')
        
        winner = get_object_or_404(Card, id=winner_id)
        loser = get_object_or_404(Card, id=loser_id)
        
        Duel.objects.create(winner=winner, loser=loser)
        update_elo(winner, loser)
        
        return redirect('rank_cards', profile_id=profile.id, card_type=card_type)

    # Fetch 2 random cards
    card1 = None
    card2 = None
    
    if card_type == 'image':
        cards = Card.objects.filter(prompt__isnull=True)
        count = cards.count()
        if count >= 2:
            random_indices = random.sample(range(count), 2)
            card1 = cards[random_indices[0]]
            card2 = cards[random_indices[1]]
            
    elif card_type == 'prompt':
        # Find prompts with at least 2 cards
        prompts_with_cards = Prompt.objects.annotate(card_count=Count('card')).filter(card_count__gte=2)
        if prompts_with_cards.exists():
            selected_prompt = random.choice(list(prompts_with_cards))
            cards = selected_prompt.card_set.all()
            if cards.count() >= 2:
                card1, card2 = random.sample(list(cards), 2)

    if not card1 or not card2:
        return render(request, 'rank.html', {'profile': profile, 'error': 'Not enough cards to rank!', 'card_type': card_type})

    return render(request, 'rank.html', {'profile': profile, 'card1': card1, 'card2': card2, 'card_type': card_type})