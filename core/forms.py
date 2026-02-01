from django import forms
from .models import Card, Prompt

class ImageCardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['image']
        labels = {
            'image': 'Last opp bilde'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True

class PromptCardForm(forms.ModelForm):
    prompt = forms.ModelChoiceField(queryset=Prompt.objects.all(), empty_label="Velg en prompt")

    class Meta:
        model = Card
        fields = ['prompt', 'answer', 'image']
        labels = {
            'answer': 'Tekstsvar',
            'image': 'Bildesvar'
        }

    def clean(self):
        cleaned_data = super().clean()
        answer = cleaned_data.get('answer')
        image = cleaned_data.get('image')

        if not answer and not image:
            raise forms.ValidationError("Du må gi enten et tekstsvar eller et bilde.")
        
        if answer and image:
             raise forms.ValidationError("Vennligst gi enten et tekstsvar ELLER et bilde, ikke begge.")
        
        return cleaned_data
