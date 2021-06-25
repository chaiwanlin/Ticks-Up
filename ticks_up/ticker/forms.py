from django import forms


class TickerForm(forms.Form):
    ticker = forms.CharField(label='Ticker', max_length=7)


class DaysForm(forms.Form):
    days = forms.IntegerField(min_value=0)


class VerticalSpreadsForm(forms.Form):
    days = forms.IntegerField(min_value=0)
    lower_bound = forms.FloatField(min_value=0)
    target_price = forms.FloatField(min_value=0)
    risk = forms.FloatField(min_value=0, max_value=100)