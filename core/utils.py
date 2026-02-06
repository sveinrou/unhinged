def calculate_elo(cards, duels, initial_rating=1200.0, k_factor=32):
    """
    Calculates ELO ratings for a set of cards based on a specific list of duels.
    Implements Vote Volume Normalization: judges who vote more have less weight per vote.
    Returns a dictionary: {card_id: {'rating': float, 'won': int, 'lost': int}}
    """
    ratings = {
        card.id: {
            'rating': initial_rating,
            'won': 0,
            'lost': 0
        } for card in cards
    }

    # 1. Pre-calculate vote counts per judge
    judge_counts = {}
    valid_judges_count = 0
    for duel in duels:
        if duel.judge:
            jid = duel.judge.id
            judge_counts[jid] = judge_counts.get(jid, 0) + 1
    
    if judge_counts:
        avg_votes = sum(judge_counts.values()) / len(judge_counts)
    else:
        avg_votes = 1

    for duel in duels:
        winner_id = duel.winner_id
        loser_id = duel.loser_id

        # Skip if cards are not in the provided set
        if winner_id not in ratings or loser_id not in ratings:
            continue

        ratings[winner_id]['won'] += 1
        ratings[loser_id]['lost'] += 1

        w_curr = ratings[winner_id]['rating']
        l_curr = ratings[loser_id]['rating']

        expected_winner = 1 / (1 + 10 ** ((l_curr - w_curr) / 400))
        expected_loser = 1 / (1 + 10 ** ((w_curr - l_curr) / 400))

        # Calculate Dynamic K-Factor
        current_k = k_factor
        if duel.judge:
            user_votes = judge_counts.get(duel.judge.id, avg_votes)
            # Weight is inverse to volume: more votes = less weight per vote
            weight = avg_votes / user_votes if user_votes > 0 else 1
            # Clamp weight to prevent extreme volatility (e.g., 0.5x to 2.5x)
            weight = max(0.5, min(weight, 2.5))
            current_k = k_factor * weight

        ratings[winner_id]['rating'] += current_k * (1 - expected_winner)
        ratings[loser_id]['rating'] += current_k * (0 - expected_loser)

    return ratings

def calculate_elo_history(cards, duels, initial_rating=1200.0, k_factor=32):
    """
    Calculates ELO history for a set of cards.
    Implements Vote Volume Normalization.
    Returns a dictionary: {card_id: [{'x': timestamp, 'y': rating}, ...]}
    """
    ratings = {card.id: initial_rating for card in cards}
    history = {card.id: [] for card in cards}
    
    # 1. Pre-calculate vote counts per judge
    judge_counts = {}
    for duel in duels:
        if duel.judge:
            jid = duel.judge.id
            judge_counts[jid] = judge_counts.get(jid, 0) + 1
            
    if judge_counts:
        avg_votes = sum(judge_counts.values()) / len(judge_counts)
    else:
        avg_votes = 1
    
    for i, duel in enumerate(duels):
        winner_id = duel.winner_id
        loser_id = duel.loser_id

        if winner_id not in ratings or loser_id not in ratings:
            continue

        w_curr = ratings[winner_id]
        l_curr = ratings[loser_id]

        expected_winner = 1 / (1 + 10 ** ((l_curr - w_curr) / 400))
        expected_loser = 1 / (1 + 10 ** ((w_curr - l_curr) / 400))

        # Calculate Dynamic K-Factor
        current_k = k_factor
        if duel.judge:
            user_votes = judge_counts.get(duel.judge.id, avg_votes)
            weight = avg_votes / user_votes if user_votes > 0 else 1
            weight = max(0.5, min(weight, 2.5))
            current_k = k_factor * weight

        # Calculate new ratings
        w_new = w_curr + current_k * (1 - expected_winner)
        l_new = l_curr + current_k * (0 - expected_loser)
        
        ratings[winner_id] = w_new
        ratings[loser_id] = l_new
        
        # Append to history with duel index
        history[winner_id].append({'x': i + 1, 'y': w_new}) 
        history[loser_id].append({'x': i + 1, 'y': l_new})

    return history
