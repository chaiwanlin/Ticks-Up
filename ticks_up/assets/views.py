from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.http import Http404
from .forms import AddPortfolioForm, TickerForm, AddStockPositionForm, AddOptionPositionForm, HedgeStockForm, EditOptionPositionForm
from .models import Portfolio, Ticker, StockPosition, OptionPosition
from instruments.stock import Stock
from hedge.hedge_main import hedge_stock
from hedge.spread_graphs import hedge_stock as hedge_stock_graph
from hedge.spread_graphs import bull_spread, bear_spread
import datetime


def user_check(user, portfolio_id):
    try:
        Portfolio.objects.get(user=user, id=portfolio_id)
        return True
    except Portfolio.DoesNotExist:
        return False


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
    return render(request, "assets/view_portfolio.html", {
        'portfolio': portfolio,
        'positions': positions,
        'tform': TickerForm,
        'sform': AddStockPositionForm,
        'oform': AddOptionPositionForm,
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
            try:
                ticker = portfolio.ticker_set.get(name=name)
            except Ticker.DoesNotExist:
                ticker = Ticker(portfolio=portfolio, name=name)
                ticker.save()
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
            try:
                ticker = portfolio.ticker_set.get(name=name)
            except Ticker.DoesNotExist:
                ticker = Ticker(portfolio=portfolio, name=name)
                ticker.save()
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
            print(request.POST.get('expiration_date'))
            option = portfolio.optionposition_set.get(
                ticker=ticker,
                call_or_put=request.POST.get('call_or_put'),
                buy_or_sell=request.POST.get('buy_or_sell'),
                expiration_date=datetime.datetime.strptime(request.POST.get('expiration_date'), '%B %d, %Y').strftime('%Y-%m-%d'),
                strike_price=request.POST.get('strike_price'),
            )
            if add_or_remove == "ADD":
                option_position = eoform.save(commit=False)
                option_position.portfolio = option.portfolio
                option_position.ticker = option.ticker
                option_position.call_or_put = option.call_or_put
                option_position.buy_or_sell = option.buy_or_sell
                option_position.expiration_date = option.expiration_date
                option_position.strike_price = option.strike_price
                option_position.save()
            else:
                option_position = OptionPosition(
                    portfolio=option.portfolio,
                    ticker=option.ticker,
                    call_or_put=option.call_or_put,
                    buy_or_sell=option.buy_or_sell,
                    expiration_date=option.expiration_date,
                    strike_price=option.strike_price,
                    total_cost=-eoform.cleaned_data['total_cost'],
                    total_contracts=-eoform.cleaned_data['total_contracts'],
                )
                option_position.save()

    return redirect(reverse('view_portfolio', args=[portfolio_id]))


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
            hedge = hedge_stock(
                ticker_name,
                average_cost,
                form.cleaned_data['risk'],
                form.cleaned_data['break_point'],
                form.cleaned_data['days'],
                form.cleaned_data['capped'],
                form.cleaned_data['target_price'],
            )

            bull_spread_max_gain = bull_spread(
                ticker_name + "-hedge-max-gain-collar",
                hedge[1]['max_gain']['strike_price'],
                hedge[1]['short_call']['strike_strike'],
                hedge[1]['max_gain']['max_profit'],
                hedge[1]['max_gain']['max_loss'],
            )
            bull_spread_min_loss = bull_spread(
                ticker_name + "-hedge-min-loss-collar",
                hedge[1]['min_loss']['strike_price'],
                hedge[1]['short_call']['strike_strike'],
                hedge[1]['min_loss']['max_profit'],
                hedge[1]['min_loss']['max_loss'],
            )

            collar_min_cost = hedge_stock_graph(
                ticker_name + "-hedge-min-cost",
                hedge[0]['min_cost']['strike_price'],
                (average_cost * 1.5),
                (average_cost * 1.5) - average_cost - hedge[0]['min_cost']['strike_premium'],
                hedge[0]['min_cost']['risk'],
            )

            collar_min_loss = hedge_stock_graph(
                ticker_name + "-hedge-min-loss",
                hedge[0]['min_loss']['strike_price'],
                (average_cost * 1.5),
                (average_cost * 1.5) - average_cost - hedge[0]['min_loss']['strike_premium'],
                hedge[0]['min_loss']['risk'],
            )

    else:
        form = HedgeStockForm()
        hedge = None

    return render(request, "assets/hedge_stock_position.html", {
        'portfolio': portfolio,
        'ticker': ticker_name,
        'form': form,
        'hedge': hedge,
        'bull_spread_max_gain': bull_spread_max_gain,
        'bull_spread_min_loss': bull_spread_min_loss,
        'collar_min_cost': collar_min_cost,
        'collar_min_loss': collar_min_loss,
    })