from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import AddPortfolioForm, TickerForm, AddStockPositionForm, AddOptionPositionForm
from .models import Portfolio, Ticker, StockPosition, OptionPosition


def user_check(user, portfolio_id):
    try:
        Portfolio.objects.get(user=user, id=portfolio_id)
        return True
    except Portfolio.DoesNotExist:
        return False


@login_required
def assets(request):
    user = request.user
    return render(request, "assets/assets.html", {'user': user})


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
