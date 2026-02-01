from django import forms
from .models import Card, Prompt

class MediaCardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['image', 'video']
        labels = {
            'image': 'Last opp bilde',
            'video': 'Last opp video'
        }

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')

        if not image and not video:
            raise forms.ValidationError("Du må laste opp enten et bilde eller en video.")
        if image and video:
            raise forms.ValidationError("Vennligst last opp enten et bilde ELLER en video, ikke begge.")
        return cleaned_data

class PromptCardForm(forms.ModelForm):
    prompt = forms.ModelChoiceField(queryset=Prompt.objects.all(), empty_label="Velg en prompt")

    class Meta:
        model = Card
        fields = ['prompt', 'answer', 'image', 'video'] # Added video
        labels = {
            'answer': 'Tekstsvar',
            'image': 'Bildesvar',
            'video': 'Videosvar' # New label
        }

    def clean(self):
        cleaned_data = super().clean()
        answer = cleaned_data.get('answer')
        image = cleaned_data.get('image')
        video = cleaned_data.get('video') # Get video field

        media_count = bool(image) + bool(video) + bool(answer)

        if media_count == 0:
            raise forms.ValidationError("Du må gi enten et tekstsvar, et bilde eller en video.")
        if media_count > 1:
            raise forms.ValidationError("Vennligst gi enten et tekstsvar, et bilde ELLER en video, ikke mer enn ett.")
        
        return cleaned_data