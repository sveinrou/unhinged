from django import forms
from .models import Card, Prompt

class ImageCardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['image']
        labels = {
            'image': 'Upload Photo'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].required = True

class PromptCardForm(forms.ModelForm):
    prompt = forms.ModelChoiceField(queryset=Prompt.objects.all(), empty_label="Select a Prompt")

    class Meta:
        model = Card
        fields = ['prompt', 'answer', 'image']
        labels = {
            'answer': 'Text Answer',
            'image': 'Image Answer'
        }

    def clean(self):
        cleaned_data = super().clean()
        answer = cleaned_data.get('answer')
        image = cleaned_data.get('image')

        if not answer and not image:
            raise forms.ValidationError("You must provide either a text answer or an image.")
        
        if answer and image:
             raise forms.ValidationError("Please provide either a text answer OR an image, not both.")
        
        return cleaned_data
