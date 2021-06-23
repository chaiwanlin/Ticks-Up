from django.contrib.auth.forms import UserCreationForm
from django import forms

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ("email",)

class SpreadsForm(forms.Form):
    ticker = forms.CharField(label='Ticker', max_length=10)
    target_price = forms.IntegerField(label='Target Price')