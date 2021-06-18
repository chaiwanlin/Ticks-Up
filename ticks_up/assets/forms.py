from django import forms
from .models import Portfolio, Position

class SpreadsForm(forms.Form):
    ticker = forms.CharField(label='Ticker', max_length=10)
    target_price = forms.IntegerField(label='Target Price')

class AddPortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        exclude = ('user',)

class AddPositionForm(forms.ModelForm):
    class Meta:
        model = Position
        exclude = ('portfolio',)