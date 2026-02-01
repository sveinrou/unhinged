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
