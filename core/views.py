from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile, Card, Duel, Prompt, Participant
from .forms import ImageCardForm, PromptCardForm
import random
from django.db.models import Count
from .utils import calculate_elo
from django.db.models import Q

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
            error = "Ugyldig passord. Vennligst prøv igjen."
            
    return render(request, 'index.html', {'error': error})

def join_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    if request.method == 'POST':
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        if name:
            # Get or create participant
            participant, created = Participant.objects.get_or_create(
                profile=profile, 
                name=name,
                defaults={'gender': gender or 'O'}
            )
            # If participant existed but logic allows updating (not strictly requested but good for safety), 
            # we keep existing data. Here we assume name is unique identifier per profile.
            
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
    
    return render(request, 'upload_card.html', {'form': form, 'profile': profile, 'title': 'Last opp bildekort'})

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
    
    return render(request, 'upload_card.html', {'form': form, 'profile': profile, 'title': 'Svar på en prompt'})

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
        
        # We just create the duel. ELO is calculated on the fly in stats view.
        Duel.objects.create(winner=winner, loser=loser, judge=participant)
        
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
        return render(request, 'rank.html', {'profile': profile, 'error': 'Ikke nok kort til å rangere!', 'card_type': card_type})

    return render(request, 'rank.html', {'profile': profile, 'card1': card1, 'card2': card2, 'card_type': card_type})

def stats(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    filter_by = request.GET.get('filter_by', 'all')
    
    # Get all cards
    cards = list(Card.objects.filter(profile=profile))
    
    # Get all duels relevant to this profile
    all_duels = list(Duel.objects.filter(winner__profile=profile).select_related('judge'))
    
    # Apply filters
    filtered_duels = []
    filter_label = "Alle rangeringer"

    if filter_by == 'all':
        filtered_duels = all_duels
    elif filter_by == 'men':
        filtered_duels = [d for d in all_duels if d.judge and d.judge.gender == 'M']
        filter_label = "Rangeringer (menn)"
    elif filter_by == 'women':
        filtered_duels = [d for d in all_duels if d.judge and d.judge.gender == 'F']
        filter_label = "Rangeringer (kvinner)"
    else:
        # Check if it's a participant ID
        try:
             p_id = int(filter_by)
             participant = get_object_or_404(Participant, id=p_id)
             filtered_duels = [d for d in all_duels if d.judge and d.judge.id == p_id]
             filter_label = f"{participant.name}s rangeringer"
        except (ValueError, Participant.DoesNotExist):
             # Fallback
             filtered_duels = all_duels
    
    # Calculate ELOs based on filtered duels
    ratings = calculate_elo(cards, filtered_duels)
    
    # Attach stats to card objects
    for card in cards:
        r = ratings.get(card.id)
        card.elo_rating = r['rating']
        card.won_count = r['won']
        card.lost_count = r['lost']
        
    # Sort by ELO
    cards.sort(key=lambda x: x.elo_rating, reverse=True)

    image_cards = [c for c in cards if c.prompt is None]
    prompt_cards = [c for c in cards if c.prompt is not None]
    
    participants = profile.participants.all().order_by('name')

    return render(request, 'stats.html', {
        'profile': profile,
        'image_cards': image_cards,
        'prompt_cards': prompt_cards,
        'filter_by': filter_by,
        'filter_label': filter_label,
        'participants': participants
    })

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
def live_dashboard(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    
    # Initial data
    image_count = Card.objects.filter(profile=profile, prompt__isnull=True).count()
    prompt_count = Card.objects.filter(profile=profile, prompt__isnull=False).count()
    duel_count = Duel.objects.filter(winner__profile=profile).count()

    return render(request, 'live_dashboard.html', {
        'profile': profile,
        'image_count': image_count,
        'prompt_count': prompt_count,
        'duel_count': duel_count
    })

@login_required
def live_dashboard_data(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    
    image_count = Card.objects.filter(profile=profile, prompt__isnull=True).count()
    prompt_count = Card.objects.filter(profile=profile, prompt__isnull=False).count()
    duel_count = Duel.objects.filter(winner__profile=profile).count()
    
    return JsonResponse({
        'image_count': image_count,
        'prompt_count': prompt_count,
        'duel_count': duel_count
    })

def final_results(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    if request.session.get('profile_id') != profile.id:
        return redirect('index')

    filter_by = request.GET.get('filter_by', 'all')

    # Fetch all cards sorted by ELO
    cards = list(Card.objects.filter(profile=profile))
    all_duels = list(Duel.objects.filter(winner__profile=profile).select_related('judge'))
    
    # Apply filters
    filtered_duels = []
    filter_label = "Alle rangeringer"

    if filter_by == 'all':
        filtered_duels = all_duels
    elif filter_by == 'men':
        filtered_duels = [d for d in all_duels if d.judge and d.judge.gender == 'M']
        filter_label = "Rangeringer (menn)"
    elif filter_by == 'women':
        filtered_duels = [d for d in all_duels if d.judge and d.judge.gender == 'F']
        filter_label = "Rangeringer (kvinner)"
    else:
        # Check if it's a participant ID
        try:
             p_id = int(filter_by)
             participant = get_object_or_404(Participant, id=p_id)
             filtered_duels = [d for d in all_duels if d.judge and d.judge.id == p_id]
             filter_label = f"{participant.name}s rangeringer"
        except (ValueError, Participant.DoesNotExist):
             # Fallback
             filtered_duels = all_duels

    ratings = calculate_elo(cards, filtered_duels)
    
    for card in cards:
        card.elo_rating = ratings[card.id]['rating']
        
    cards.sort(key=lambda x: x.elo_rating, reverse=True)

    # Separate
    images = [c for c in cards if c.prompt is None]
    all_prompts = [c for c in cards if c.prompt is not None]
    
    # Filter unique prompts (highest rated only)
    seen_prompts = set()
    prompts = []
    for card in all_prompts:
        if card.prompt.id not in seen_prompts:
            prompts.append(card)
            seen_prompts.add(card.prompt.id)

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
    
    participants = profile.participants.all().order_by('name')

    return render(request, 'final_results.html', {
        'profile': profile, 
        'final_list': final_list,
        'participants': participants,
        'filter_by': filter_by,
        'filter_label': filter_label
    })