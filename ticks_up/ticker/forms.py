from django import forms


class VerticalSpreadsForm(forms.Form):
    days = forms.IntegerField(min_value=0)
    lower_bound = forms.FloatField(min_value=0)
    target_price = forms.FloatField(min_value=0)
    risk = forms.FloatField(min_value=0, max_value=100)