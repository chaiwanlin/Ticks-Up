import math
import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.http import Http404, HttpResponse
from django.forms import formset_factory
from .forms import *
from .models import *
from hedge_instruments.stock import Stock
from hedge_functions.spread import hedge_stock, collar
from utils.graphs import draw_graph
from portfolio_functions.industry import Industry as Classification
from portfolio_functions.portfolio_instrument import *
from portfolio_functions.position import *


def user_check(user, portfolio_id):
    try:
        Portfolio.objects.get(user=user, id=portfolio_id)
        return True
    except Portfolio.DoesNotExist:
        return False


def ticker_check(symbol):
    try:
        ticker = Ticker.objects.get(name=symbol)
    except Ticker.DoesNotExist:
        classification = Classification(symbol)
        print(symbol)
        sector = Sector(name=classification.get_sector())
        industry = Industry(name=classification.get_industry(), sector=sector)
        # sector = Sector(name='Sex')
        # industry = Industry(name='Nuggets', sector=sector)
        sector.save()
        industry.save()
        ticker = Ticker(name=symbol, sector=sector, industry=industry)
        ticker.save()
    return ticker


@login_required
def assets(request):
    user = request.user
    return render(request, "assets/assets.html", {
        'user': user,
        'form': AddPortfolioForm,
    })


@login_required
def add_portfolio(request):
    if request.method == 'POST':
        form = AddPortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect(reverse('assets'))

    else:
        form = AddPortfolioForm()

    return render(request, "assets/add_portfolio.html", {'form': form})


@login_required
def remove_portfolio(request, portfolio_id):
    if user_check(request.user, portfolio_id):
        Portfolio.objects.get(id=portfolio_id).delete()

    return redirect(reverse('assets'))


@login_required
def view_portfolio(request, portfolio_id):
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    portfolio = Portfolio.objects.get(id=portfolio_id)
    tickers = portfolio.ticker_set.all()
    stock_positions = portfolio.stockposition_set.all()
    option_positions = portfolio.optionposition_set.all()
    positions = {}
    for t in tickers:
        try:
            stock = stock_positions.get(ticker=t)
        except StockPosition.DoesNotExist:
            stock = StockPosition.objects.none()

        options = option_positions.filter(ticker=t)
        positions[t.name] = (stock, options)

    # Portfolio sorting
    # for stock_pos in stock_positions:


    return render(request, "assets/view_portfolio.html", {
        'portfolio': portfolio,
        'positions': positions,
        'tform': TickerForm,
        'sform': AddStockPositionForm,
        'oform': AddOptionPositionForm,
        'vsform': AddVerticalSpreadForm,
        'vseform': AddVerticalSpreadExtraForm,
        'bsform': AddButterflySpreadForm,
        'bseform': AddButterflySpreadExtraForm,
        'cform': AddCollarForm,
        'ppform': AddProtectivePutForm,
        'hedge_stock_form': HedgeStockForm,
        'eoform': EditOptionPositionForm,
    })


@login_required
def add_stock_position(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        tform = TickerForm(request.POST)
        sform = AddStockPositionForm(request.POST)
        if tform.is_valid() and sform.is_valid():
            name = tform.cleaned_data['name'].upper()
            ticker = ticker_check(name)
            ticker.portfolio.add(portfolio)
            stock_position = sform.save(commit=False)
            stock_position.portfolio = portfolio
            stock_position.ticker = ticker
            stock_position.save()
            return redirect(reverse('view_portfolio', args=[portfolio_id]))

    else:
        tform = TickerForm()
        sform = AddStockPositionForm()

    return render(request, "assets/add_stock_position.html", {
        'tform': tform,
        'sform': sform,
        'portfolio': portfolio
    })


@login_required
def edit_stock_position(request, portfolio_id, ticker_name, add_or_remove):
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        sform = AddStockPositionForm(request.POST)
        if sform.is_valid():
            portfolio = Portfolio.objects.get(id=portfolio_id)
            ticker = portfolio.ticker_set.get(name=ticker_name)
            if add_or_remove == "ADD":
                stock_position = sform.save(commit=False)
                stock_position.portfolio = portfolio
                stock_position.ticker = ticker
                stock_position.save()
            else:
                stock_position = StockPosition(
                    portfolio=portfolio,
                    ticker=ticker,
                    total_cost=-sform.cleaned_data['total_cost'],
                    total_shares=-sform.cleaned_data['total_shares']
                )
                stock_position.save()

    return redirect(reverse('view_portfolio', args=[portfolio_id]))


@login_required
def add_option_position(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        tform = TickerForm(request.POST)
        oform = AddOptionPositionForm(request.POST)
        if tform.is_valid() and oform.is_valid():
            name = tform.cleaned_data['name'].upper()
            ticker = ticker_check(name)
            ticker.portfolio.add(portfolio)
            option_position = oform.save(commit=False)
            option_position.portfolio = portfolio
            option_position.ticker = ticker
            option_position.save()
            return redirect(reverse('view_portfolio', args=[portfolio_id]))

    else:
        tform = TickerForm()
        oform = AddOptionPositionForm()

    return render(request, "assets/add_option_position.html", {
        'tform': tform,
        'oform': oform,
        'portfolio': portfolio
    })


@login_required
def edit_option_position(request, portfolio_id, ticker_name, add_or_remove):
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        eoform = EditOptionPositionForm(request.POST)
        if eoform.is_valid():
            portfolio = Portfolio.objects.get(id=portfolio_id)
            ticker = portfolio.ticker_set.get(name=ticker_name)
            print(request.POST.get('strike_price'))
            option = portfolio.optionposition_set.get(
                ticker=ticker,
                call_or_put=request.POST.get('call_or_put'),
                long_or_short=request.POST.get('long_or_short'),
                expiration_date=datetime.datetime.strptime(request.POST.get('expiration_date'), '%b. %d, %Y').strftime('%Y-%m-%d'),
                strike_price=request.POST.get('strike_price'),
            )
            if add_or_remove == "ADD":
                option_position = eoform.save(commit=False)
                option_position.portfolio = option.portfolio
                option_position.ticker = option.ticker
                option_position.call_or_put = option.call_or_put
                option_position.long_or_short = option.long_or_short
                option_position.expiration_date = option.expiration_date
                option_position.strike_price = option.strike_price
                option_position.save()
            else:
                option_position = OptionPosition(
                    portfolio=option.portfolio,
                    ticker=option.ticker,
                    call_or_put=option.call_or_put,
                    long_or_short=option.long_or_short,
                    expiration_date=option.expiration_date,
                    strike_price=option.strike_price,
                    total_cost=-eoform.cleaned_data['total_cost'],
                    total_contracts=-eoform.cleaned_data['total_contracts'],
                )
                option_position.save()

    return redirect(reverse('view_portfolio', args=[portfolio_id]))


@login_required
def add_vertical_spread(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        tform = TickerForm(request.POST)
        vsform = AddVerticalSpreadForm(request.POST)
        vseform = AddVerticalSpreadExtraForm(request.POST)
        if tform.is_valid() and vsform.is_valid() and vseform.is_valid():
            name = tform.cleaned_data['name'].upper()
            ticker = ticker_check(name)
            ticker.portfolio.add(portfolio)

            type = vsform.cleaned_data['types']
            credit_or_debit = vsform.cleaned_data['credit_or_debit']

            expiration_date = vseform.cleaned_data['expiration_date']
            quantity = vseform.cleaned_data['quantity']

            if (type == 'BULL' and credit_or_debit == 'DEBIT') or (type == 'BEAR' and credit_or_debit == 'CREDIT'):
                short_leg = OptionPosition(
                    portfolio=portfolio,
                    ticker=ticker,
                    call_or_put='CALL',
                    long_or_short='SHORT',
                    expiration_date=expiration_date,
                    strike_price=vseform.cleaned_data['short_leg_strike'],
                    total_cost=vseform.cleaned_data['short_leg_premium'] * quantity,
                    total_contracts=quantity
                )
                long_leg = OptionPosition(
                    portfolio=portfolio,
                    ticker=ticker,
                    call_or_put='CALL',
                    long_or_short='LONG',
                    expiration_date=expiration_date,
                    strike_price=vseform.cleaned_data['long_leg_strike'],
                    total_cost=vseform.cleaned_data['long_leg_premium'] * quantity,
                    total_contracts=quantity
                )
            else:
                short_leg = OptionPosition(
                    portfolio=portfolio,
                    ticker=ticker,
                    call_or_put='PUT',
                    long_or_short='SHORT',
                    expiration_date=expiration_date,
                    strike_price=vseform.cleaned_data['short_leg_strike'],
                    total_cost=vseform.cleaned_data['short_leg_premium'] * quantity,
                    total_contracts=quantity
                )
                long_leg = OptionPosition(
                    portfolio=portfolio,
                    ticker=ticker,
                    call_or_put='PUT',
                    long_or_short='LONG',
                    expiration_date=expiration_date,
                    strike_price=vseform.cleaned_data['long_leg_strike'],
                    total_cost=vseform.cleaned_data['long_leg_premium'] * quantity,
                    total_contracts=quantity
                )
            short_leg.save()
            long_leg.save()

            vs = vsform.save(commit=False)
            vs.portfolio = portfolio
            vs.ticker = ticker
            vs.short_leg = short_leg
            vs.long_leg = long_leg
            vs.save()
            return redirect(reverse('view_portfolio', args=[portfolio_id]))

    else:
        tform = TickerForm
        vsform = AddVerticalSpreadForm
        vseform = AddVerticalSpreadExtraForm

    return HttpResponse("<h1>You don't belong here</h1>")


@login_required
def add_butterfly_spread(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        tform = TickerForm(request.POST)
        bsform = AddButterflySpreadForm(request.POST)
        bseform = AddButterflySpreadExtraForm(request.POST)
        if tform.is_valid() and bsform.is_valid() and bseform.is_valid():
            name = tform.cleaned_data['name'].upper()
            ticker = ticker_check(name)
            ticker.portfolio.add(portfolio)

            type = bsform.cleaned_data['types']
            expiration_date = bseform.cleaned_data['expiration_date']
            quantity = bseform.cleaned_data['quantity']

            long_put = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='PUT',
                long_or_short='LONG',
                expiration_date=expiration_date,
                strike_price=bseform.cleaned_data['long_put_strike'],
                total_cost=bseform.cleaned_data['long_put_premium'] * quantity,
                total_contracts=quantity
            )
            short_put = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='PUT',
                long_or_short='SHORT',
                expiration_date=expiration_date,
                strike_price=bseform.cleaned_data['short_put_strike'],
                total_cost=bseform.cleaned_data['short_put_premium'] * quantity,
                total_contracts=quantity
            )
            short_call = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='CALL',
                long_or_short='SHORT',
                expiration_date=expiration_date,
                strike_price=bseform.cleaned_data['short_call_strike'],
                total_cost=bseform.cleaned_data['short_call_premium'] * quantity,
                total_contracts=quantity
            )
            long_call = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='CALL',
                long_or_short='LONG',
                expiration_date=expiration_date,
                strike_price=bseform.cleaned_data['long_call_strike'],
                total_cost=bseform.cleaned_data['long_call_premium'] * quantity,
                total_contracts=quantity
            )
            long_put.save()
            short_put.save()
            short_call.save()
            long_call.save()

            bull_spread = VerticalSpread(
                portfolio=portfolio,
                ticker=ticker,
                types='BULL',
                credit_or_debit='CREDIT',
                short_leg=short_put,
                long_leg=long_put
            )
            bear_spread = VerticalSpread(
                portfolio=portfolio,
                ticker=ticker,
                types='BEAR',
                credit_or_debit='CREDIT',
                short_leg=short_call,
                long_leg=long_call
            )
            bull_spread.save()
            bear_spread.save()

            bs = bsform.save(commit=False)
            bs.portfolio = portfolio
            bs.ticker = ticker
            bs.bull_spread = bull_spread
            bs.bear_spread = bear_spread
            bs.save()
            return redirect(reverse('view_portfolio', args=[portfolio_id]))

    else:
        tform = TickerForm
        bsform = AddButterflySpreadForm
        bseform = AddButterflySpreadExtraForm

    return HttpResponse("<h1>You don't belong here</h1>")


@login_required
def add_collar(request, portfolio_id, ticker_name):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        cform = AddCollarForm(request.POST)
        if cform.is_valid():
            ticker = ticker_check(ticker_name)
            ticker.portfolio.add(portfolio)

            expiration_date = cform.cleaned_data['expiration_date']
            quantity = cform.cleaned_data['quantity']

            try:
                stock = portfolio.stockposition_set.get(ticker=ticker)
                total_shares = getattr(stock, 'total_shares')
                if total_shares <= (quantity * 100):
                    return Http404()
            except StockPosition.DoesNotExist:
                return Http404()

            long_put = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='PUT',
                long_or_short='LONG',
                expiration_date=expiration_date,
                strike_price=cform.cleaned_data['long_put_strike'],
                total_cost=cform.cleaned_data['long_put_premium'] * quantity,
                total_contracts=quantity
            )
            short_call = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='CALL',
                long_or_short='SHORT',
                expiration_date=expiration_date,
                strike_price=cform.cleaned_data['short_call_strike'],
                total_cost=cform.cleaned_data['short_call_premium'] * quantity,
                total_contracts=quantity
            )
            long_put.save()
            short_call.save()

            collar = Collar(
                portfolio=portfolio,
                ticker=ticker,
                stock_position=stock,
                long_put=long_put,
                short_call=short_call,
            )
            collar.save()
            return redirect(reverse('view_portfolio', args=[portfolio_id]))

    else:
        cform = AddCollarForm

    return HttpResponse("<h1>You don't belong here</h1>")


@login_required
def add_protective_put(request, portfolio_id, ticker_name):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        ppform = AddProtectivePutForm(request.POST)
        if ppform.is_valid():
            ticker = ticker_check(ticker_name)
            ticker.portfolio.add(portfolio)

            expiration_date = ppform.cleaned_data['expiration_date']
            quantity = ppform.cleaned_data['quantity']

            try:
                stock = portfolio.stockposition_set.get(ticker=ticker)
                total_shares = getattr(stock, 'total_shares')
                if total_shares <= (quantity * 100):
                    return Http404()
            except StockPosition.DoesNotExist:
                return Http404()

            long_put = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='PUT',
                long_or_short='LONG',
                expiration_date=expiration_date,
                strike_price=ppform.cleaned_data['long_put_strike'],
                total_cost=ppform.cleaned_data['long_put_premium'] * quantity,
                total_contracts=quantity
            )
            long_put.save()

            protective_put = ProtectivePut(
                portfolio=portfolio,
                ticker=ticker,
                stock_position=stock,
                long_put=long_put,
            )
            protective_put.save()
            return redirect(reverse('view_portfolio', args=[portfolio_id]))

    else:
        ppform = AddProtectivePutForm

    return HttpResponse("<h1>You don't belong here</h1>")


@login_required
def hedge_stock_position(request, portfolio_id, ticker_name):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    ticker = portfolio.ticker_set.get(name=ticker_name)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('view_portfolio', args=[portfolio_id]))

    try:
        stock = Stock(ticker)
    except LookupError:
        raise Http404("Ticker does not exist")

    if request.method == 'POST':
        form = HedgeStockForm(request.POST)
        if form.is_valid():
            stock_position = portfolio.stockposition_set.get(ticker=ticker)
            average_cost = float(stock_position.total_cost / stock_position.total_shares)
            risk = form.cleaned_data['risk']
            break_point = form.cleaned_data['break_point']
            days = form.cleaned_data['days']
            capped = form.cleaned_data['capped']
            target_price = form.cleaned_data['target_price']
            hedge = {}
            if capped:
                hedge['protective_put'] = hedge_stock(ticker_name, average_cost, risk, break_point, days, capped,
                                                target_price)
                hedge['collar'] = collar(ticker, days, average_cost, break_point, target_price, risk)
            else:
                hedge['protective_put'] = hedge_stock(ticker_name, average_cost, risk, break_point, days, capped,
                                                target_price)
            max_price_limit = -math.inf
            coordinate_lists = []
            for strat in hedge:
                if hedge[strat]['graph']['price_limit'] > max_price_limit:
                    max_price_limit = hedge[strat]['graph']['price_limit']
                coordinate_lists += (hedge[strat]['graph']['coordinate_lists'])
            graph = draw_graph(price_limit=max_price_limit, coordinate_lists=coordinate_lists)

    else:
        form = HedgeStockForm()
        hedge = None

    return render(request, "assets/hedge_stock_position.html", {
        'portfolio': portfolio,
        'ticker': ticker_name,
        'form': form,
        'hedge': hedge,
        'risk': risk,
        'break_point': break_point,
        'days': days,
        'capped': capped,
        'target_price': target_price,
        'graph': graph,
    })