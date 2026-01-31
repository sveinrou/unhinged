def update_elo(winner, loser, k_factor=32):
    expected_winner = 1 / (1 + 10 ** ((loser.elo_rating - winner.elo_rating) / 400))
    expected_loser = 1 / (1 + 10 ** ((winner.elo_rating - loser.elo_rating) / 400))
    
    winner.elo_rating += k_factor * (1 - expected_winner)
    loser.elo_rating += k_factor * (0 - expected_loser)
    
    winner.save()
    loser.save()
