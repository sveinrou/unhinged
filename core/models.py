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
    password = models.CharField(max_length=128, blank=True, help_text="Leave blank to auto-generate an 8-letter password.") 
    results_available = models.BooleanField(default=False, help_text="Check this to reveal the results buttons to users.")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = ''.join(random.choices(string.ascii_lowercase, k=8))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Participant(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other/Prefer not to say'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='participants')
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('profile', 'name')

    def __str__(self):
        return f"{self.name} ({self.profile.name})"

class Card(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='cards', null=True)
    uploader = models.ForeignKey(Participant, on_delete=models.SET_NULL, null=True, blank=True, related_name='cards')
    image = models.ImageField(upload_to='card_images/', blank=True, null=True)
    prompt = models.ForeignKey(Prompt, on_delete=models.SET_NULL, null=True, blank=True)
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        prompt_text = self.prompt.text if self.prompt else "No Prompt"
        return f"{self.profile.name} - {prompt_text}: {self.answer}"

class Duel(models.Model):
    winner = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='won_duels')
    loser = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='lost_duels')
    judge = models.ForeignKey(Participant, on_delete=models.SET_NULL, null=True, blank=True, related_name='judged_duels')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Winner: {self.winner.id} vs Loser: {self.loser.id}"