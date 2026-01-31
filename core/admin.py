from django.contrib import admin
from .models import Card, Prompt, Profile, Duel, Participant

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'password', 'created_at')

admin.site.register(Card)
admin.site.register(Prompt)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Duel)
admin.site.register(Participant)