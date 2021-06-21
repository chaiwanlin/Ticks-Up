from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import CustomUserCreationForm, SpreadsForm
from .src.hedge.hedge1 import get_options

def home(request):
    if request.method == 'POST':
        form = SpreadsForm(request.POST)
        if form.is_valid():
            ticker = form.cleaned_data['ticker']
            target_price = form.cleaned_data['target_price']
            return redirect(reverse('ticker', args=(ticker, target_price,)))

    else:
        form = SpreadsForm()

    return render(request, "users/home.html", {'form': form})


def register(request):
    if request.method == "GET":
        return render(
            request, "users/register.html",
            {"form": CustomUserCreationForm}
        )
    elif request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse('home'))


def ticker(request, ticker, target_price):
    spreads = get_options(ticker, float(target_price))
    return render(request, "users/ticker.html", {
        'ticker': ticker.upper(),
        'debit_spread': spreads['debit_spread'],
        'credit_spread': spreads['credit_spread']
    })