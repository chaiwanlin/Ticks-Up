from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import AddPortfolioForm, AddStockPositionForm, AddOptionPositionForm
from .models import Portfolio, StockPosition, OptionPosition

@login_required
def assets(request):
    user = request.user
    portfolio_list = Portfolio.objects.filter(user=user)
    return render(request, "assets.html", {'portfolio_list': portfolio_list})

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

    return render(request, "add_portfolio.html", {'form': form})

@login_required
def view_portfolio(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    stock_positions = StockPosition.objects.filter(portfolio=portfolio)
    option_positions = OptionPosition.objects.filter(portfolio=portfolio)
    return render(request, "view_portfolio.html", {
        'portfolio': portfolio,
        'stock_positions': stock_positions,
        'option_positions': option_positions
    })

@login_required
def add_stock_position(request, portfolio_id):
    if request.method == 'POST':
        form = AddStockPositionForm(request.POST)
        if form.is_valid():
            stock_position = form.save(commit=False)
            portfolio = Portfolio.objects.get(id=portfolio_id)
            stock_position.portfolio = portfolio
            stock_position.save()
            return redirect(reverse('view_portfolio', args=[portfolio_id]))

    else:
        form = AddStockPositionForm()

    return render(request, "add_stock_position.html", {'form': form, 'portfolio_id': portfolio_id})


@login_required
def add_option_position(request, portfolio_id):
    if request.method == 'POST':
        form = AddOptionPositionForm(request.POST)
        if form.is_valid():
            option_position = form.save(commit=False)
            portfolio = Portfolio.objects.get(id=portfolio_id)
            option_position.portfolio = portfolio
            option_position.save()
            return redirect(reverse('view_portfolio', args=[portfolio_id]))

    else:
        form = AddOptionPositionForm()

    return render(request, "add_option_position.html", {'form': form, 'portfolio_id': portfolio_id})
