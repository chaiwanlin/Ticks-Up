from django import forms


class TickerForm(forms.Form):
    ticker = forms.CharField(label='Ticker', max_length=7)


# class VerticalSpreadsForm(forms.Form):