from django import forms

from .models import Chat

class ChatForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ('title', 'text')
        widgets = {
            'title': forms.TextInput(attr={'class': 'form-control my-5'}),
            'text': forms.Textarea(attr={'class': 'form-control my-5'})
        }
        label = {
            'text': 'How can I help you today?'
        }