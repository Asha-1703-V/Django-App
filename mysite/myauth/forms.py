from django import forms
from .models import Profile

class UpdateAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar',)