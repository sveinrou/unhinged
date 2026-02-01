def calculate_elo(cards, duels, initial_rating=1200.0, k_factor=32):
    """
    Calculates ELO ratings for a set of cards based on a specific list of duels.
    Returns a dictionary: {card_id: {'rating': float, 'won': int, 'lost': int}}
    """
    ratings = {
        card.id: {
            'rating': initial_rating,
            'won': 0,
            'lost': 0
        } for card in cards
    }

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

        ratings[winner_id]['rating'] += k_factor * (1 - expected_winner)
        ratings[loser_id]['rating'] += k_factor * (0 - expected_loser)

    return ratings

def calculate_elo_history(cards, duels, initial_rating=1200.0, k_factor=32):
    """
    Calculates ELO history for a set of cards.
    Returns a dictionary: {card_id: [{'x': timestamp, 'y': rating}, ...]}
    """
    # Initialize history with starting point (we don't have a start time, so maybe just first duel time or empty?)
    # Let's just record changes. Chart.js can handle it.
    
    # Current ratings
    ratings = {card.id: initial_rating for card in cards}
    
    # History: card_id -> list of points
    history = {card.id: [] for card in cards}
    
    for i, duel in enumerate(duels): # Enumerate duels to get index
        winner_id = duel.winner_id
        loser_id = duel.loser_id

        if winner_id not in ratings or loser_id not in ratings:
            continue

        w_curr = ratings[winner_id]
        l_curr = ratings[loser_id]

        expected_winner = 1 / (1 + 10 ** ((l_curr - w_curr) / 400))
        expected_loser = 1 / (1 + 10 ** ((w_curr - l_curr) / 400))

        # Calculate new ratings
        w_new = w_curr + k_factor * (1 - expected_winner)
        l_new = l_curr + k_factor * (0 - expected_loser)
        
        ratings[winner_id] = w_new
        ratings[loser_id] = l_new
        
        # Append to history with duel index
        history[winner_id].append({'x': i + 1, 'y': w_new}) # Duel index (1-based)
        history[loser_id].append({'x': i + 1, 'y': l_new})

    return history
