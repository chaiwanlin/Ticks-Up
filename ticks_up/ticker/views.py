from django.shortcuts import render, redirect, reverse
from django.http import Http404
from .forms import DaysForm, VerticalSpreadsForm
from instruments.stock import Stock
from hedge.hedge_main import historical_volatility, volatility_skew, get_iv, put_call_ratio, range_to_date, hedge_stock
from hedge import spread


def home(request):
    # if request.method == 'POST':
    #     form = forms.TickerForm(request.POST)
    #     if form.is_valid():
    #         ticker = form.cleaned_data['ticker'].upper()
    #         return redirect(reverse('ticker', args=(ticker,)))
    #
    # else:
    #     form = forms.TickerForm()
    #
    # return render(request, "ticker/home.html", {'form': form})

    # if request.method == 'POST':
    #     ticker_name = request.POST.get('ticker').upper()
    #     try:
    #         stock = Stock(ticker_name)
    #     except LookupError:
    #         raise Http404("Ticker does not exist")
    #     return redirect(reverse(search_ticker, args=[ticker_name]))
    #
    # else:
    #     return render(request, "ticker/home.html", {})

    return render(request, "ticker/home.html", {})


def search_ticker(request):
    if request.method == 'GET':
        ticker = request.GET.get('ticker').upper()
        try:
            stock = Stock(ticker)
        except LookupError:
            raise Http404("Ticker does not exist")

        try:
            form = DaysForm(request.GET)
            days = int(form.cleaned_data['days'])
        except AttributeError:
            days = 30

        ticker_data = {}
        ticker_data['Historical Volatility'] = historical_volatility(ticker)
        ticker_data['Volatility Skew'] = volatility_skew(ticker)
        ticker_data['Implied Volatility'] = get_iv(ticker, days)
        ticker_data['Put-Call Ratio'] = put_call_ratio(ticker, days)
        # ticker_data['range_to_date'] = range_to_date(ticker, days)

        return render(request, "ticker/search_ticker.html", {
            'ticker': ticker,
            'form': DaysForm(),
            'days': days,
            'ticker_data': ticker_data,
        })

    else:
        return redirect(reverse(home))
    # try:
    #     stock = Stock(ticker)
    # except LookupError:
    #     raise Http404("Ticker does not exist")
    #
    # if request.method == 'POST':
    #     form = DaysForm(request.POST)
    #     if form.is_valid():
    #         days = form.cleaned_data['days']
    #
    # else:
    #     form = DaysForm()
    #     days = 30
    #
    # ticker_data = {}
    # ticker_data['historical_volatility'] = historical_volatility(ticker)
    # ticker_data['volatility_skew'] = volatility_skew(ticker)
    # ticker_data['iv'] = get_iv(ticker, days)
    # ticker_data['put_call_ratio'] = put_call_ratio(ticker, days)
    # # ticker_data['range_to_date'] = range_to_date(ticker, days)
    #
    # return render(request, "ticker/ticker.html", {
    #     'ticker': ticker,
    #     'form': form,
    #     'days': days,
    #     'ticker_data': ticker_data,
    # })


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
        form = VerticalSpreadsForm(request.POST)
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
        form = VerticalSpreadsForm()

    return render(request, "ticker/vertical_spread.html", {
        'ticker': ticker,
        'form': form,
        'spreads': spreads,
    })