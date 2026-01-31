from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Card, Duel, Prompt, Participant
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
            # Redirect to join page instead of home
            return redirect('join_profile', profile_id=profile.id)
        except Profile.DoesNotExist:
            error = "Invalid password. Please try again."
            
    return render(request, 'index.html', {'error': error})

def join_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            # Get or create participant
            participant, created = Participant.objects.get_or_create(profile=profile, name=name)
            request.session['participant_id'] = participant.id
            return redirect('profile_home', profile_id=profile.id)
            
    return render(request, 'join_profile.html', {'profile': profile})

def profile_home(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    # Simple security check
    if request.session.get('profile_id') != profile.id:
         return redirect('index')
    
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return redirect('join_profile', profile_id=profile.id)
    
    participant = get_object_or_404(Participant, id=participant_id)
    
    return render(request, 'profile_home.html', {'profile': profile, 'participant': participant})

def upload_image_card(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    participant_id = request.session.get('participant_id')
    if not participant_id:
        return redirect('join_profile', profile_id=profile.id)
    participant = get_object_or_404(Participant, id=participant_id)

    if request.method == 'POST':
        form = ImageCardForm(request.POST, request.FILES)
        if form.is_valid():
            card = form.save(commit=False)
            card.profile = profile
            card.uploader = participant
            card.save()
            return redirect('profile_home', profile_id=profile.id)
    else:
        form = ImageCardForm()
    
    return render(request, 'upload_card.html', {'form': form, 'profile': profile, 'title': 'Upload Photo Card'})

def upload_prompt_card(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    participant_id = request.session.get('participant_id')
    if not participant_id:
        return redirect('join_profile', profile_id=profile.id)
    participant = get_object_or_404(Participant, id=participant_id)

    if request.method == 'POST':
        form = PromptCardForm(request.POST, request.FILES)
        if form.is_valid():
            card = form.save(commit=False)
            card.profile = profile
            card.uploader = participant
            card.save()
            return redirect('profile_home', profile_id=profile.id)
    else:
        form = PromptCardForm()
    
    return render(request, 'upload_card.html', {'form': form, 'profile': profile, 'title': 'Answer a Prompt'})

def rank_cards(request, profile_id, card_type):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    participant_id = request.session.get('participant_id')
    if not participant_id:
         return redirect('join_profile', profile_id=profile.id)
    participant = get_object_or_404(Participant, id=participant_id)

    if request.method == 'POST':
        winner_id = request.POST.get('winner')
        loser_id = request.POST.get('loser')
        
        winner = get_object_or_404(Card, id=winner_id)
        loser = get_object_or_404(Card, id=loser_id)
        
        Duel.objects.create(winner=winner, loser=loser, judge=participant)
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

def stats(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    # distinct=True is used to avoid duplicate counting when joining multiple relations
    cards = Card.objects.annotate(
        won_count=Count('won_duels', distinct=True), 
        lost_count=Count('lost_duels', distinct=True)
    ).order_by('-elo_rating')

    image_cards = cards.filter(prompt__isnull=True)
    prompt_cards = cards.filter(prompt__isnull=False)

    return render(request, 'stats.html', {
        'profile': profile,
        'image_cards': image_cards,
        'prompt_cards': prompt_cards
    })

def final_results(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    # Fetch all cards sorted by ELO
    images = list(Card.objects.filter(profile=profile, prompt__isnull=True).order_by('-elo_rating'))
    prompts = list(Card.objects.filter(profile=profile, prompt__isnull=False).order_by('-elo_rating'))

    # Defined pattern: 1. photo, 2. prompt, 3. photo, 4. photo, 5. prompt, 6. photo, 7. prompt, 8. photo
    pattern = ['image', 'prompt', 'image', 'image', 'prompt', 'image', 'prompt', 'image']
    final_list = []

    img_idx = 0
    pmt_idx = 0

    for item_type in pattern:
        if item_type == 'image':
            if img_idx < len(images):
                final_list.append(images[img_idx])
                img_idx += 1
        elif item_type == 'prompt':
            if pmt_idx < len(prompts):
                final_list.append(prompts[pmt_idx])
                pmt_idx += 1

    return render(request, 'final_results.html', {'profile': profile, 'final_list': final_list})