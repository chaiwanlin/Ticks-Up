from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import AddPortfolioForm, AddPositionForm
from .models import Portfolio, Position

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
    position_list = Position.objects.filter(portfolio=portfolio)
    return render(request, "view_portfolio.html", {'portfolio': portfolio, 'position_list': position_list})

@login_required
def add_position(request, portfolio_id):
    if request.method == 'POST':
        form = AddPositionForm(request.POST)
        if form.is_valid():
            portfolio = Portfolio.objects.get(id=portfolio_id)
            position = form.save(commit=False)
            position.portfolio = portfolio
            position.save()
            return redirect(reverse('assets'))

    else:
        form = AddPositionForm()

    return render(request, "add_position.html", {'form': form})
