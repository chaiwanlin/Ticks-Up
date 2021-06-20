from django import forms
from django.core.exceptions import ValidationError
from .models import Portfolio, StockPosition, OptionPosition
# from .src.instruments import instrument, stock, option
from wallstreet import Stock, Call, Put


class SpreadsForm(forms.Form):
    ticker = forms.CharField(label='Ticker', max_length=10)
    target_price = forms.IntegerField(label='Target Price')


class AddPortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        exclude = ('user',)


class AddStockPositionForm(forms.ModelForm):
    class Meta:
        model = StockPosition
        exclude = ('portfolio',)

    def clean_ticker(self):
        ticker = self.cleaned_data['ticker']
        try:
            test = Stock(ticker)
            return ticker.upper()
        except:     #fill in error
            raise ValidationError("Invalid ticker!")


class AddOptionPositionForm(forms.ModelForm):
    class Meta:
        model = OptionPosition
        exclude = ('portfolio',)

    def clean_ticker(self):
        ticker = self.cleaned_data['ticker']
        try:
            test = Stock(ticker)
            return ticker.upper()
        except:  # fill in error
            raise ValidationError("Invalid ticker!")

        # ticker = self.cleaned_data['ticker']
        # call_or_put = self.cleaned_data['call_or_put']
        # buy_or_sell = self.cleaned_data['buy_or_sell']
        # expiration_date = self.cleaned_data['expiration_date']
        # strike_price = self.cleaned_data['strike_price']
        # try:
        #     if call_or_put == "CALL":
        #         test = Call(
        #             ticker.upper(),
        #             d=expiration_date.day,
        #             m=expiration_date.month,
        #             y=expiration_date.year,
        #             strike=strike_price)
        #     else:
        #         test = Put(
        #             ticker.upper(),
        #             d=expiration_date.day,
        #             m=expiration_date.month,
        #             y=expiration_date.year,
        #             strike=strike_price)
        #     return ticker.upper()
        # except:  # fill in error
        #     raise ValidationError("Invalid ticker!")