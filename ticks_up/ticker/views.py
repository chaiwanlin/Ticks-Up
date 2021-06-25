from django.shortcuts import render, redirect, reverse
from django.http import Http404
from . import forms
from .src_new.instruments.stock import Stock


def home(request):
    if request.method == 'POST':
        form = forms.TickerForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker'].upper()
            return redirect(reverse('ticker', args=(ticker,)))

    else:
        form = forms.TickerForm()

    return render(request, "ticker/home.html", {'form': form})


def ticker(request, ticker):
    try:
        stock = Stock(ticker)
    except LookupError:
        raise Http404("Ticker does not exist")

    return render(request, "ticker/ticker.html", {
        'ticker': ticker,
        'stock': stock,
    })


# def vertical_spreads(request, ticker):
#
