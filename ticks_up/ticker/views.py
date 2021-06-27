from django.shortcuts import render, redirect, reverse
from django.http import Http404
from . import forms
from .src_new.instruments.stock import Stock
from src.hedge.hedge_main import historical_volatility, volatility_skew, get_iv, put_call_ratio, range_to_date, hedge_stock
from src.hedge import spread


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

    if request.method == 'POST':
        form = forms.DaysForm(request.POST)
        if form.is_valid():
            days = form.cleaned_data['days']

    else:
        form = forms.DaysForm()
        days = 30

    ticker_data = {}
    ticker_data['historical_volatility'] = historical_volatility(ticker)
    ticker_data['volatility_skew'] = volatility_skew(ticker)
    ticker_data['iv'] = get_iv(ticker, days)
    ticker_data['put_call_ratio'] = put_call_ratio(ticker, days)
    # ticker_data['range_to_date'] = range_to_date(ticker, days)

    return render(request, "ticker/ticker.html", {
        'ticker': ticker,
        'form': form,
        'days': days,
        'ticker_data': ticker_data,
    })


def vertical_spreads(request, ticker):
    try:
        stock = Stock(ticker)
    except LookupError:
        raise Http404("Ticker does not exist")

    spreads = {
        'debit_spread': None,
        'credit_spread': None,
    }

    if request.method == 'POST':
        form = forms.VerticalSpreadsForm(request.POST)
        if form.is_valid():
            days = form.cleaned_data['days']
            lower_bound = form.cleaned_data['lower_bound']
            target_price = form.cleaned_data['target_price']
            risk = form.cleaned_data['risk']
            if target_price > stock.get_price():
                spreads['debit_spread'] = spread.bull_debit_spread(ticker, days, lower_bound, target_price, risk)
                spreads['credit_spread'] = spread.bull_credit_spread(ticker, days, lower_bound, target_price, risk)
            else:
                spreads['debit_spread'] = spread.bear_debit_spread(ticker, days, lower_bound, target_price, risk)
                spreads['credit_spread'] = spread.bear_credit_spread(ticker, days, lower_bound, target_price, risk)

    else:
        form = forms.VerticalSpreadsForm()

    return render(request, "ticker/vertical_spread.html", {
        'ticker': ticker,
        'form': form,
        'spreads': spreads,
    })