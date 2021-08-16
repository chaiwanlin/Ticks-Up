from django import forms
from django.core.exceptions import ValidationError
from .models import *
from hedge_instruments.stock import Stock
from hedge_instruments.option import *
import datetime
from portfolio_functions.industry import Industry as Classification


class AddPortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        exclude = ('user',)


class CashForm(forms.Form):
    amount = forms.DecimalField(max_digits=19, decimal_places=2, min_value=0)


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
            Stock(ticker)
            return ticker.upper()

        except LookupError:
            raise ValidationError("Invalid ticker!")


class AddStockPositionForm(forms.ModelForm):
    class Meta:
        model = StockPosition
        exclude = ('portfolio', 'ticker', 'long_or_short')


class AddOptionPositionForm(forms.ModelForm):
    class Meta:
        model = OptionPosition
        exclude = ('portfolio', 'ticker')
        widgets = {
            'expiration_date': forms.widgets.DateInput(attrs={'type': 'date'}),
        }


class EditOptionPositionForm(forms.ModelForm):
    class Meta:
        model = OptionPosition
        fields = ['average_price', 'total_contracts']


class AddVerticalSpreadForm(forms.ModelForm):

    class Meta:
        model = VerticalSpread
        fields = ['types', 'credit_or_debit']


class AddVerticalSpreadExtraForm(forms.Form):
    expiration_date = forms.DateField(initial=datetime.date.today, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    quantity = forms.IntegerField(min_value=1)

    short_leg_strike = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    long_leg_strike = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    short_leg_premium = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    long_leg_premium = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])


class AddButterflySpreadForm(forms.ModelForm):
    class Meta:
        model = ButterflySpread
        fields = ['types']


class AddButterflySpreadExtraForm(forms.Form):
    expiration_date = forms.DateField(initial=datetime.date.today, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    quantity = forms.IntegerField(min_value=1)

    long_put_strike = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    short_put_strike = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    short_call_strike = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    long_call_strike = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    long_put_premium = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    short_put_premium = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    short_call_premium = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    long_call_premium = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])


class AddCollarForm(forms.Form):
    expiration_date = forms.DateField(initial=datetime.date.today, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    quantity = forms.IntegerField(min_value=1)

    long_put_strike = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    short_call_strike = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    long_put_premium = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    short_call_premium = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])


class AddProtectivePutForm(forms.Form):
    expiration_date = forms.DateField(initial=datetime.date.today, widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    quantity = forms.IntegerField(min_value=1)

    long_put_strike = forms.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(Decimal('0.01'))])
    long_put_premium = forms.DecimalField(max_digits=10, decimal_places=1, validators=[MinValueValidator(Decimal('0.01'))])


class HedgeStockForm(forms.Form):
    days = forms.IntegerField(min_value=0, help_text="Number of days away the options will expire")
    lower_bound = forms.FloatField(min_value=0, help_text="Expected lower bound of price action by number of days stated above")
    upper_bound = forms.FloatField(min_value=0, help_text="Expected upper bound of price action by number of days stated above")
    risk = forms.FloatField(min_value=0, max_value=100, help_text="(Maximum amount you are willing to risk) / 100")
    capped = forms.BooleanField(initial=True, required=False, help_text="Capped or uncapped profit")