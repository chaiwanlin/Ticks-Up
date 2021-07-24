from django import forms


class OptionStrategiesForm(forms.Form):
    days = forms.IntegerField(min_value=0, help_text="Number of days away the options will expire.")
    lower_bound = forms.FloatField(min_value=0, help_text="Expected lower bound of price action by number of days stated above.")
    target_price = forms.FloatField(min_value=0, help_text="Expected upper bound of price action by number of days stated above.")
    risk = forms.FloatField(min_value=0, max_value=100, help_text="(Maximum amount you are willing to risk) / 100.")