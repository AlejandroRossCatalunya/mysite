from django import forms
from .models import Profile


class UserAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["avatar"]