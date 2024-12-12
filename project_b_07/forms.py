from django import forms
from .models import Team, TeamMembership, TeamFile, TeamChatMessage


class TeamCreationForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            }

class TeamFileUploadForm(forms.ModelForm):
    class Meta:
        model = TeamFile
        fields = ['title', 'file', 'description', 'keywords']

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = TeamChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message...'}),
        }
