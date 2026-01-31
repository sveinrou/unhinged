from django.core.management.base import BaseCommand
from core.models import Card, Duel
from core.utils import update_elo

class Command(BaseCommand):
    help = 'Recalculates ELO ratings for all cards based on existing duels.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--initial-elo',
            type=float,
            default=1200.0,
            help='Initial ELO rating to reset all cards to (default: 1200.0)',
        )

    def handle(self, *args, **options):
        initial_elo = options['initial_elo']
        
        self.stdout.write(self.style.WARNING(f'Resetting all cards to ELO {initial_elo}...'))
        
        # Reset all cards
        Card.objects.all().update(elo_rating=initial_elo)
        
        duels = Duel.objects.all().order_by('created_at')
        count = duels.count()
        
        self.stdout.write(f'Replaying {count} duels...')
        
        for i, duel in enumerate(duels, 1):
            # Refetch to get updated ratings from previous iterations
            winner = Card.objects.get(id=duel.winner.id)
            loser = Card.objects.get(id=duel.loser.id)
            
            update_elo(winner, loser)
            
            if i % 10 == 0:
                self.stdout.write(f'Processed {i}/{count} duels...')

        self.stdout.write(self.style.SUCCESS('Successfully recalculated ELO ratings.'))
