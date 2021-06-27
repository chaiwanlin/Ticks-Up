from django import forms
from django.core.exceptions import ValidationError
from .models import Portfolio, Ticker, StockPosition, OptionPosition
# from .src-old-hedge1.instruments import instrument, stock, option
from wallstreet import Stock, Call, Put


class AddPortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        exclude = ('user',)


class TickerForm(forms.ModelForm):
    class Meta:
        model = Ticker
        exclude = ('portfolio',)

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


class HedgeStockForm(forms.Form):
    risk = forms.FloatField(min_value=0, max_value=100)
    break_point = forms.FloatField(min_value=0)
    days = forms.IntegerField(min_value=0)
    capped = forms.BooleanField()
    target_price = forms.FloatField(min_value=0)