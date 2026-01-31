from django.db import models
import random
import string

class Prompt(models.Model):
    text = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Profile(models.Model):
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=128, blank=True, help_text="Leave blank to auto-generate an 8-letter password.") # For simple entrance, not full authentication
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = ''.join(random.choices(string.ascii_lowercase, k=8))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Card(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='cards', null=True)
    image = models.ImageField(upload_to='card_images/', blank=True, null=True)
    prompt = models.ForeignKey(Prompt, on_delete=models.SET_NULL, null=True, blank=True)
    answer = models.TextField(blank=True, null=True)
    elo_rating = models.FloatField(default=1200.0)
    submitted_by = models.CharField(max_length=100, blank=True) # Name of person who made this card
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        prompt_text = self.prompt.text if self.prompt else "No Prompt"
        return f"{self.profile.name} - {prompt_text}: {self.answer}"

class Duel(models.Model):
    winner = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='won_duels')
    loser = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='lost_duels')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Winner: {self.winner.id} vs Loser: {self.loser.id}"
