from django import forms
from django.core.exceptions import ValidationError
from .models import *
from hedge_instruments.stock import Stock


class AddPortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        exclude = ('user',)


class TickerForm(forms.ModelForm):
    class Meta:
        model = Ticker
        fields = ['name']
        labels = {
            'name': 'Ticker'
        }

    def clean_ticker(self):
        ticker = self.cleaned_data['name']
        try:
            test = Stock(ticker)
            return ticker.upper()
        except:     #fill in error
            raise ValidationError("Invalid ticker!")


class AddStockPositionForm(forms.ModelForm):
    class Meta:
        model = StockPosition
        exclude = ('portfolio', 'ticker')


class AddOptionPositionForm(forms.ModelForm):
    class Meta:
        model = OptionPosition
        exclude = ('portfolio', 'ticker')
        labels = {
            'expiration_date': 'Expiration date (YYYY-MM-DD)'
        }

    # clean option data for validation


class EditOptionPositionForm(forms.ModelForm):
    class Meta:
        model = OptionPosition
        fields = ['total_cost', 'total_contracts']

    # clean option data for validation


class AddVerticalSpreadForm(forms.ModelForm):
    class Meta:
        model = VerticalSpread
        fields = ['types', 'credit_or_debit']


class AddButterflySpreadForm(forms.ModelForm):
    class Meta:
        model = ButterflySpread
        fields = ['types']


class HedgeStockForm(forms.Form):
    risk = forms.FloatField(min_value=0, max_value=100)
    break_point = forms.FloatField(min_value=0)
    days = forms.IntegerField(min_value=0)
    capped = forms.BooleanField(initial=True, required=False)
    target_price = forms.FloatField(min_value=0)