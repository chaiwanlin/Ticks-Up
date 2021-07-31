import math
from django.shortcuts import render, redirect, reverse
from django.http import Http404, JsonResponse
from .forms import *
from hedge_instruments.stock import Stock
from hedge_functions.hedge_main import *
from hedge_functions import spread
from utils.graphs import draw_graph
from assets.models import Ticker
from portfolio_functions.industry import Industry
from portfolio_functions.industry_constants import *
from background_task import background


def home(request):
    return render(request, "ticker/home.html", {})


def search_ticker(request):
    if request.method == 'GET':
        ticker = request.GET.get('ticker').upper()
        ticker_set = Ticker.objects.filter(name=ticker)
        if not ticker_set:
            try:
                stock = Stock(ticker)
            except LookupError:
                raise Http404("Ticker does not exist")

            try:
                ticker_info = Industry(ticker)
                sector = ticker_info.get_sector()
                industry = ticker_info.get_industry()
            except LookupError:
                error = "Not Available"
                sector = error
                industry = error
        else:
            stock = Stock(ticker)
            ticker_obj = Ticker.objects.get(name=ticker)
            sector = ticker_obj.sector.name
            industry = ticker_obj.industry.name


        days = request.GET.get('days')
        if not days:
            days = 30
        else:
            days = int(days)

        ticker_data = {}

        # ticker_data['Historical Volatility'] = "We're working on it..."

        try:
            ticker_data['Volatility Skew'] = round(volatility_skew(ticker, days), 4)
        except (KeyError, ZeroDivisionError) as e:
            ticker_data['Implied Volatility'] = "Not available right now"
        except LookupError:
            ticker_data['Implied Volatility'] = "Not available for this stock"

        try:
            ticker_data['Implied Volatility'] = round(get_iv(ticker, days), 4)
        except (KeyError, ZeroDivisionError) as e:
            ticker_data['Implied Volatility'] = "Not available right now"
        except LookupError:
            ticker_data['Implied Volatility'] = "Not available for this stock"

        try:
            ticker_data['Put-Call Ratio'] = round(put_call_ratio(ticker, days), 4)
        except (KeyError, ZeroDivisionError) as e:
            ticker_data['Put-Call Ratio'] = "Not available right now"
        except LookupError:
            ticker_data['Put-Call Ratio'] = "Not available for this stock"

        return render(request, "ticker/search_ticker.html", {
            'ticker': ticker,
            'exchange': stock.get_exchange(),
            'sector': sector,
            'industry': industry,
            'days': days,
            'ticker_data': ticker_data,
            'option_strategies_form': OptionStrategiesForm,
            'view_similar_tickers_form': ViewSimilarTickersForm,
        })

    else:
        return redirect(reverse(home))


@background()
def view_similar_tickers(request, ticker, sector_or_industry):
    try:
        stock = Stock(ticker)
    except LookupError:
        raise Http404("Ticker does not exist")

    if request.method == 'POST':
        form = ViewSimilarTickersForm(request.POST)
        if form.is_valid():
            ticker_info = Industry(ticker)
            indicator_value = form.cleaned_data['indicator']
            k = form.cleaned_data['number']

        else:
            ticker_info = Industry(ticker)
            indicator_value = request.POST.get('indicator')
            k = request.POST.get('number')

        category = None
        indicator_name = None
        indicator = None
        for cat, indic_dict in CATEGORIES_INDICATORS_DICT.items():
            for indic, val in indic_dict.items():
                if indicator_value == val[0]:
                    category = cat
                    indicator_name = indic
                    indicator = val

        if not category:
            raise Http404("Ticker does not exist")

        if sector_or_industry == 'SECTOR':
            result = ticker_info.get_k_closest_same_sector(k, category, indicator)
        else:
            result = ticker_info.get_k_closest_same_industry(k, category, indicator)

        return render(request, "ticker/view_similar_tickers.html", {
            'ticker': ticker,
            'sector_or_industry': sector_or_industry,
            'form': ViewSimilarTickersForm,
            'indicators': LIST_OF_INDICATORS,
            'indicator_value': indicator_value,
            'indicator_name': indicator_name,
            'indicator': indicator,
            'k': k,
            'result': result,
        })

    return redirect(reverse('search_ticker'))


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