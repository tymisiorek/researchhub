# roadmap/forms.py

from django import forms
from .models import Milestone
from django.core.exceptions import ValidationError

class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'start_date', 'end_date', 'progress']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        """Ensure the end date is not before the start date and progress is between 0 and 100."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        progress = cleaned_data.get('progress')

        if start_date and end_date:
            if end_date < start_date:
                self.add_error('end_date', 'End date cannot be before start date.')

        if progress is not None:
            if not (0 <= progress <= 100):
                self.add_error('progress', 'Progress must be between 0 and 100.')