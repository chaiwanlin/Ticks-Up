import math
from django.shortcuts import render, redirect, reverse
from django.http import Http404, JsonResponse
from .forms import OptionStrategiesForm
from instruments.stock import Stock
from hedge.hedge_main import historical_volatility, volatility_skew, get_iv, put_call_ratio, range_to_date, hedge_stock
from hedge import spread
from utility.graphs import draw_graph


def home(request):
    return render(request, "ticker/home.html", {})


def search_ticker(request):
    if request.method == 'GET':
        ticker = request.GET.get('ticker').upper()
        try:
            stock = Stock(ticker)
        except LookupError:
            raise Http404("Ticker does not exist")

        days = request.GET.get('days')
        if not days:
            days = 30
        else:
            days = int(days)

        ticker_data = {}
        # ticker_data['Historical Volatility'] = historical_volatility(ticker)
        # ticker_data['Volatility Skew'] = volatility_skew(ticker)
        ticker_data['Historical Volatility'] = "We're working on it..."
        ticker_data['Volatility Skew'] = "We're working on it..."
        try:
            ticker_data['Implied Volatility'] = get_iv(ticker, days)
        except ZeroDivisionError:
            ticker_data['Implied Volatility'] = "Not available right now"

        try:
            ticker_data['Put-Call Ratio'] = put_call_ratio(ticker, days)
        except ZeroDivisionError:
            ticker_data['Put-Call Ratio'] = "Not available right now"

        return render(request, "ticker/search_ticker.html", {
            'ticker': ticker,
            'exchange': stock.get_exchange(),
            'days': days,
            'ticker_data': ticker_data,
            'option_strategies_form': OptionStrategiesForm,
        })

    else:
        return redirect(reverse(home))


def option_strategies(request, ticker):
    try:
        stock = Stock(ticker)
    except LookupError:
        raise Http404("Ticker does not exist")

    spreads = {
    }

    if request.method == 'POST':
        form = OptionStrategiesForm(request.POST)
        if form.is_valid():
            days = form.cleaned_data['days']
            lower_bound = form.cleaned_data['lower_bound']
            target_price = form.cleaned_data['target_price']
            risk = form.cleaned_data['risk']
            if target_price > stock.get_price() and lower_bound > stock.get_price():
                spreads['debit_spread'] = spread.bull_debit_spread(ticker, days, lower_bound, target_price, risk)
                spreads['credit_spread'] = spread.bull_credit_spread(ticker, days, lower_bound, target_price, risk)

            elif target_price < stock.get_price() and lower_bound < stock.get_price():
                spreads['debit_spread'] = spread.bear_debit_spread(ticker, days, lower_bound, target_price, risk)
                spreads['credit_spread'] = spread.bear_credit_spread(ticker, days, lower_bound, target_price, risk)

            elif target_price > stock.get_price() and lower_bound < stock.get_price():
                spreads['iron_condor'] = spread.iron_condor(ticker, days, lower_bound, target_price, risk)

            max_price_limit = -math.inf
            coordinate_lists = []
            for strat in spreads:
                if spreads[strat]['graph']['price_limit'] > max_price_limit:
                    max_price_limit = spreads[strat]['graph']['price_limit']
                coordinate_lists += (spreads[strat]['graph']['coordinate_lists'])
            graph = draw_graph(price_limit=max_price_limit, coordinate_lists=coordinate_lists)


    else:
        form = OptionStrategiesForm()

    return render(request, "ticker/option_strategies.html", {
        'ticker': ticker,
        'form': form,
        'days': days,
        'lower_bound': lower_bound,
        'target_price': target_price,
        'risk': risk,
        'spreads': spreads,
        'graph': graph,
    })