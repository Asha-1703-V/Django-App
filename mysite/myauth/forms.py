from django import forms
from .models import UserProfile

class UpdateAvatarForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('avatar',)