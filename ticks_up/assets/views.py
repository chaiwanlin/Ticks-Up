from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import AddPortfolioForm, AddStockPositionForm, AddOptionPositionForm
from .models import Portfolio, StockPosition, OptionPosition


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
    return render(request, "assets/view_portfolio.html", {
        'portfolio': portfolio,
    })

@login_required
def add_stock_position(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        form = AddStockPositionForm(request.POST)
        if form.is_valid():
            stock_position = form.save(commit=False)
            stock_position.portfolio = portfolio
            stock_position.save()
            return redirect(reverse('view_portfolio', args=[portfolio_id]))

    else:
        form = AddStockPositionForm()

    return render(request, "assets/add_stock_position.html", {'form': form, 'portfolio': portfolio})


@login_required
def add_option_position(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        form = AddOptionPositionForm(request.POST)
        if form.is_valid():
            option_position = form.save(commit=False)
            option_position.portfolio = portfolio
            option_position.save()
            return redirect(reverse('view_portfolio', args=[portfolio_id]))

    else:
        form = AddOptionPositionForm()

    return render(request, "assets/add_option_position.html", {'form': form, 'portfolio': portfolio})
