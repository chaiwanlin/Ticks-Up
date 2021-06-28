from django.shortcuts import render, redirect, reverse
from django.http import Http404
from .forms import VerticalSpreadsForm
from instruments.stock import Stock
from hedge.hedge_main import historical_volatility, volatility_skew, get_iv, put_call_ratio, range_to_date, hedge_stock
from hedge import spread
from hedge.spread_graphs import bull_spread, bear_spread


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
        ticker_data['Implied Volatility'] = get_iv(ticker, days)
        ticker_data['Put-Call Ratio'] = put_call_ratio(ticker, days)

        return render(request, "ticker/search_ticker.html", {
            'ticker': ticker,
            'days': days,
            'ticker_data': ticker_data,
            'vertical_spreads_form': VerticalSpreadsForm,
        })

    else:
        return redirect(reverse(home))


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
                bull_spread(
                    ticker + "-debit-spread-max-gain",
                    spreads['debit_spread']['max_gain']['strike_price'],
                    spreads['debit_spread']['short_call']['strike_strike'],
                    spreads['debit_spread']['max_gain']['max_profit'],
                    spreads['debit_spread']['max_gain']['max_loss'],
                )
                bull_spread(
                    ticker + "-debit-spread-min-cost",
                    spreads['debit_spread']['min_cost']['strike_price'],
                    spreads['debit_spread']['short_call']['strike_strike'],
                    spreads['debit_spread']['min_cost']['max_profit'],
                    spreads['debit_spread']['min_cost']['max_loss'],
                )

                bull_spread(
                    ticker + "-credit-spread-max-gain",
                    spreads['credit_spread']['max_gain']['strike_price'],
                    spreads['credit_spread']['short_put']['strike_strike'],
                    spreads['credit_spread']['max_gain']['max_profit'],
                    spreads['credit_spread']['max_gain']['max_loss'],
                )
                bull_spread(
                    ticker + "-credit-spread-min-loss",
                    spreads['credit_spread']['min_loss']['strike_price'],
                    spreads['credit_spread']['short_put']['strike_strike'],
                    spreads['credit_spread']['min_loss']['max_profit'],
                    spreads['credit_spread']['min_loss']['max_loss'],
                )


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