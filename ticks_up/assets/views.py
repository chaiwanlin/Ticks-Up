import math
import datetime
import decimal
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.http import Http404, HttpResponse
from .forms import *
from .models import *
from hedge_instruments.stock import Stock as StockHedge
from hedge_functions.spread import hedge_stock, collar
from utils.graphs import draw_graph, make_pie
from portfolio_functions.industry import Industry as Classification
import portfolio_functions.portfolio_instrument as pi
from portfolio_functions.position import OverallPosition as OverallPos
from portfolio_functions.position import StockPosition as StockPos
from portfolio_functions.position import OptionPosition as OptionPos
from portfolio_functions.user_portfolio import *


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
        try:
            classification = Classification(symbol)
        except LookupError:
            raise LookupError("Invalid ticker!")
        sector_name = classification.get_sector()
        industry_name = classification.get_industry()

        try:
            sector = Sector.objects.get(name=sector_name)
        except Sector.DoesNotExist:
            sector = Sector(name=sector_name)
            sector.save()

        try:
            industry = Industry.objects.get(name=industry_name)
        except Industry.DoesNotExist:
            industry = Industry(name=industry_name, sector=sector)
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
    if portfolio.margin:
        margin = True
    else:
        margin = False
    tickers = portfolio.ticker_set.all()
    stock_positions = portfolio.stockposition_set.all()
    option_positions = portfolio.optionposition_set.all()
    positions = {}
    positions_for_view = {}

    list_of_overall_pos = []
    industries = {}
    sectors = {}
    list_of_sector_portfolios = []
    for t in tickers:
        # Buid positions for current template
        try:
            stock = stock_positions.get(ticker=t)
        except StockPosition.DoesNotExist:
            stock = StockPosition.objects.none()

        options = option_positions.filter(ticker=t)
        positions[t.name] = (stock, options)

        # Build User Portfolio
        build_of_overall_pos = build_overall_pos(portfolio, t)
        positions_for_view[t.name] = build_of_overall_pos[1]
        overall_pos = build_of_overall_pos[0]
        list_of_overall_pos.append(overall_pos)

        if t.industry.name not in industries:
            industries[t.industry.name] = [overall_pos]
        else:
            industries[t.industry.name].append(overall_pos)

        if t.sector.name not in sectors:
            sectors[t.sector.name] = [overall_pos]
        else:
            sectors[t.sector.name].append(overall_pos)

    for industry, list_of_tickers in industries.items():
        industries[industry] = Industry_Portfolio(industry, list_of_tickers, margin)

    for sector, list_of_tickers in sectors.items():
        list_of_industries = []
        for industry, industry_portfolio in industries.items():
            if Industry.objects.get(name=industry).sector.name == sector:
                list_of_industries.append(industry_portfolio)

        list_of_sector_portfolios.append(Sector_Portfolio(sector, list_of_industries, list_of_tickers, margin))

    user_portfolio = User_Portfolio(list_of_overall_pos, portfolio.cash, margin, list_of_sector_portfolios)
    try:
        portfolio_breakdown = {
            'portfolio_level': {
                'ticker_breakdown': user_portfolio.breakdown_by_ticker(),
                'ticker_breakdown_graph': make_pie(user_portfolio.breakdown_by_ticker(), "Ticker Breakdown"),
                # 'ticker_average': user_portfolio.average_ticker_weight(),
                'sector_breakdown': user_portfolio.breakdown_by_sectors(),
                'sector_breakdown_graph': make_pie(user_portfolio.breakdown_by_sectors(), "Sector Breakdown"),
                # 'sector_average': (user_portfolio.average_sector_weight()),
                'sector_level': {},
            }
        }
        sector_level = portfolio_breakdown['portfolio_level']['sector_level']
        for sector in user_portfolio.sectors:
            sector_level[sector.id] = {
                'ticker_breakdown': sector.breakdown_by_ticker(),
                'ticker_breakdown_graph': make_pie(sector.breakdown_by_ticker(), "Ticker Breakdown"),
                # 'ticker_average': sector.average_ticker_weight(),
                'industry_breakdown': sector.breakdown_by_industry(),
                'industry_breakdown_graph': make_pie(sector.breakdown_by_industry(), "Industry Breakdown"),
                # 'industry_average': sector.average_industry_weight(),
                'industry_level': {}
            }

            industry_level = sector_level[sector.id]['industry_level']
            for industry in sector.industries:
                industry_level[industry.id] = {
                    # 'ticker_breakdown': industry.breakdown_by_ticker(),
                    'ticker_breakdown_graph': make_pie(industry.breakdown_by_ticker(), "Ticker Breakdown"),
                    # 'ticker_average': industry.average_ticker_weight(),
                }
    except ZeroDivisionError:
       portfolio_breakdown = {}

    return render(request, "assets/view_portfolio.html", {
        'portfolio': portfolio,
        'positions': positions,
        'positions_for_view': positions_for_view,
        'portfolio_breakdown': portfolio_breakdown,
        'cashform': CashForm,
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


def build_overall_pos(portfolio, t):
    position_for_view = {'stock_position': None,
                         'option_positions': {
                             'butterfly_spreads': None,
                             'collars': None,
                             'protective_puts': None,
                             'vertical_spreads': [],
                             'naked_options': [],
                         }
    }
    try:
        stock = portfolio.stockposition_set.get(ticker=t)
        stock_position = make_stock(stock)
        if portfolio.margin:
            stock_pos = StockPos(t.name, [stock_position], [], True, portfolio.margin)
        else:
            stock_pos = StockPos(t.name, [stock_position], [], False)
    except StockPosition.DoesNotExist:
        stock = StockPosition.objects.none()
        if portfolio.margin:
            stock_pos = StockPos(t.name, [], [], True, portfolio.margin)
        else:
            stock_pos = StockPos(t.name, [], [], False)
    position_for_view['stock_position'] = stock

    spread_list = []

    butterfly_spreads = portfolio.butterflyspread_set.filter(ticker=t)
    position_for_view['option_positions']['butterfly_spreads'] = butterfly_spreads
    for bs in butterfly_spreads:
        spread = pi.Condor(bs.types,
                           make_vertical_spread(bs.bull_spread),
                           make_vertical_spread(bs.bear_spread))
        spread_list.append(spread)

    collars = portfolio.collar_set.filter(ticker=t)
    position_for_view['option_positions']['collars'] = collars
    for c in collars:
        spread_list.append(pi.Collar(make_stock(c.stock_position),
                                     make_option(c.long_put),
                                     make_option(c.short_call)))

    protective_puts = portfolio.protectiveput_set.filter(ticker=t)
    position_for_view['option_positions']['protective_puts'] = protective_puts
    for pp in protective_puts:
        spread_list.append(pi.HedgedStock(make_stock(pp.stock_position), make_option(pp.long_put)))

    # Check if vertical spread has been used before
    for vs in portfolio.verticalspread_set.filter(ticker=t):
        solo = True

        for bs in portfolio.butterflyspread_set.filter(ticker=t):
            if vs == bs.bull_spread or vs == bs.bear_spread:
                solo = False
                break

        if solo:
            spread_list.append(make_vertical_spread(vs))
            position_for_view['option_positions']['vertical_spreads'].append(vs)


    option_lists = {
        'short_call': [],
        'long_call': [],
        'short_put': [],
        'long_put': []
    }
    for option in portfolio.optionposition_set.filter(ticker=t):
        solo = True

        for vs in portfolio.verticalspread_set.filter(ticker=t):
            if option == vs.short_leg or option == vs.long_leg:
                solo = False
                break

        for c in portfolio.collar_set.filter(ticker=t):
            if option == c.short_call or option == c.long_put:
                solo = False
                break

        for pp in portfolio.protectiveput_set.filter(ticker=t):
            if option == pp.long_put:
                solo = False
                break

        if solo:
            op = make_option(option)
            if option.long_or_short == 'SHORT':
                if option.call_or_put == 'CALL':
                    option_lists['short_call'].append(op)
                else:
                    option_lists['short_put'].append(op)
            else:
                if option.call_or_put == 'CALL':
                    option_lists['long_call'].append(op)
                else:
                    option_lists['long_put'].append(op)
            position_for_view['option_positions']['naked_options'].append(option)

    if portfolio.margin:
        option_pos = OptionPos(
            t.name,
            option_lists['short_call'],
            option_lists['long_call'],
            option_lists['short_put'],
            option_lists['long_put'],
            spread_list,
            True,
            portfolio.margin
        )
    else:
        option_pos = OptionPos(
            t.name,
            option_lists['short_call'],
            option_lists['long_call'],
            option_lists['short_put'],
            option_lists['long_put'],
            spread_list,
            False
        )

    return (
        OverallPos(
            t.name,
            stock_pos,
            option_pos,
            t.sector.name,
            t.industry.name,
        ),
        position_for_view
    )


def make_stock(stock_pos):
    return pi.Stock(stock_pos.ticker.name,
                 stock_pos.long_or_short,
                 float(stock_pos.total_shares),
                 float(stock_pos.average_price))


def make_option(option_pos):
    if option_pos.call_or_put == 'CALL':
        option = pi.Call(
            option_pos.ticker.name,
            option_pos.long_or_short,
            option_pos.total_contracts,
            float(option_pos.average_price),
            float(option_pos.strike_price),
            option_pos.expiration_date
        )
    else:
        option = pi.Put(
            option_pos.ticker.name,
            option_pos.long_or_short,
            option_pos.total_contracts,
            float(option_pos.average_price),
            float(option_pos.strike_price),
            option_pos.expiration_date
        )
    return option


def make_vertical_spread(vs):
    if vs.types == 'BULL':
        vspread = pi.Bull(
            vs.credit_or_debit,
            make_option(vs.short_leg),
            make_option(vs.long_leg)
        )
    else:
        vspread = pi.Bear(
            vs.credit_or_debit,
            make_option(vs.short_leg),
            make_option(vs.long_leg)
        )
    return vspread


@login_required
def edit_cash(request, portfolio_id, add_or_remove):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        cashform = CashForm(request.POST)
        if cashform.is_valid():
            if add_or_remove == 'ADD':
                portfolio.cash += cashform.cleaned_data['amount']
            else:
                portfolio.cash -= cashform.cleaned_data['amount']
            portfolio.save()

    return redirect(reverse('view_portfolio', args=[portfolio_id]))


@login_required
def add_stock_position(request, portfolio_id):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('assets'))
    if request.method == 'POST':
        tform = TickerForm(request.POST)
        try:
            sform = AddStockPositionForm(request.POST)
        except LookupError:
            raise Http404()
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
                    average_price=-sform.cleaned_data['average_price'],
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
            try:
                option_position.save()
            except LookupError:
                raise Http404("Option position is not valid!")
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
                    average_price=-eoform.cleaned_data['average_price'],
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
                    average_price=vseform.cleaned_data['short_leg_premium'],
                    total_contracts=quantity
                )
                long_leg = OptionPosition(
                    portfolio=portfolio,
                    ticker=ticker,
                    call_or_put='CALL',
                    long_or_short='LONG',
                    expiration_date=expiration_date,
                    strike_price=vseform.cleaned_data['long_leg_strike'],
                    average_price=vseform.cleaned_data['long_leg_premium'],
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
                    average_price=vseform.cleaned_data['short_leg_premium'],
                    total_contracts=quantity
                )
                long_leg = OptionPosition(
                    portfolio=portfolio,
                    ticker=ticker,
                    call_or_put='PUT',
                    long_or_short='LONG',
                    expiration_date=expiration_date,
                    strike_price=vseform.cleaned_data['long_leg_strike'],
                    average_price=vseform.cleaned_data['long_leg_premium'],
                    total_contracts=quantity
                )
            short_leg.save()
            long_leg.save()

            vs = vsform.save(commit=False)
            vs.portfolio = portfolio
            vs.ticker = ticker
            vs.short_leg = short_leg
            vs.long_leg = long_leg
            vs.quantity = quantity
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
                average_price=bseform.cleaned_data['long_put_premium'],
                total_contracts=quantity
            )
            short_put = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='PUT',
                long_or_short='SHORT',
                expiration_date=expiration_date,
                strike_price=bseform.cleaned_data['short_put_strike'],
                average_price=bseform.cleaned_data['short_put_premium'],
                total_contracts=quantity
            )
            short_call = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='CALL',
                long_or_short='SHORT',
                expiration_date=expiration_date,
                strike_price=bseform.cleaned_data['short_call_strike'],
                average_price=bseform.cleaned_data['short_call_premium'],
                total_contracts=quantity
            )
            long_call = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='CALL',
                long_or_short='LONG',
                expiration_date=expiration_date,
                strike_price=bseform.cleaned_data['long_call_strike'],
                average_price=bseform.cleaned_data['long_call_premium'],
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
            bs.quantity = quantity
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
                    raise Http404()
            except StockPosition.DoesNotExist:
                raise Http404()

            long_put = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='PUT',
                long_or_short='LONG',
                expiration_date=expiration_date,
                strike_price=cform.cleaned_data['long_put_strike'],
                average_price=cform.cleaned_data['long_put_premium'],
                total_contracts=quantity
            )
            short_call = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='CALL',
                long_or_short='SHORT',
                expiration_date=expiration_date,
                strike_price=cform.cleaned_data['short_call_strike'],
                average_price=cform.cleaned_data['short_call_premium'],
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
                quantity=quantity,
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
                    raise Http404()
            except StockPosition.DoesNotExist:
                raise Http404()

            long_put = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='PUT',
                long_or_short='LONG',
                expiration_date=expiration_date,
                strike_price=ppform.cleaned_data['long_put_strike'],
                average_price=ppform.cleaned_data['long_put_premium'],
                total_contracts=quantity
            )
            long_put.save()

            protective_put = ProtectivePut(
                portfolio=portfolio,
                ticker=ticker,
                stock_position=stock,
                long_put=long_put,
                quantity=quantity,
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
        stock = StockHedge(ticker)
    except LookupError:
        raise Http404("Ticker does not exist")

    hedge = {}

    if request.method == 'POST':
        form = HedgeStockForm(request.POST)
        if form.is_valid():
            stock_position = portfolio.stockposition_set.get(ticker=ticker)
            average_cost = float(stock_position.average_price)
            days = form.cleaned_data['days']
            lower_bound = form.cleaned_data['lower_bound']
            upper_bound = form.cleaned_data['upper_bound']
            risk = form.cleaned_data['risk']
            capped = form.cleaned_data['capped']
            if capped:
                hedge['protective_put'] = hedge_stock(ticker_name, average_cost, risk, lower_bound, days, capped,
                                                upper_bound)
                hedge['collar'] = collar(ticker, days, average_cost, lower_bound, upper_bound, risk)
            else:
                hedge['protective_put'] = hedge_stock(ticker_name, average_cost, risk, lower_bound, days, capped,
                                                upper_bound)
            max_price_limit = -math.inf
            coordinate_lists = []
            for strat in hedge:
                if hedge[strat]['graph']['price_limit'] > max_price_limit:
                    max_price_limit = hedge[strat]['graph']['price_limit']
                coordinate_lists += (hedge[strat]['graph']['coordinate_lists'])
            graph = draw_graph(price_limit=max_price_limit, coordinate_lists=coordinate_lists)

    else:
        raise Http404()

    form = HedgeStockForm()

    return render(request, "assets/hedge_stock_position.html", {
        'portfolio': portfolio,
        'ticker': ticker_name,
        'form': form,
        'hedge': hedge,
        'days': days,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'risk': risk,
        'capped': capped,
        'graph': graph,
    })


@login_required
def add_hedge_stock_position(request, portfolio_id, ticker_name):
    portfolio = Portfolio.objects.get(id=portfolio_id)
    ticker = portfolio.ticker_set.get(name=ticker_name)
    if not user_check(request.user, portfolio_id):
        return redirect(reverse('view_portfolio', args=[portfolio_id]))

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        strategy = request.POST.get('strategy_name')

        # Verify enough stocks to do stock hedge
        try:
            stock = portfolio.stockposition_set.get(ticker=ticker)
            total_shares = getattr(stock, 'total_shares')
            if total_shares < (quantity * 100):
                raise Http404()
        except StockPosition.DoesNotExist:
            raise Http404()

        if strategy == 'protective_put':
            long_put = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='PUT',
                long_or_short='LONG',
                expiration_date=request.POST.get('expiration_date'),
                strike_price=decimal.Decimal(request.POST.get('strike_price')),
                average_price=decimal.Decimal(request.POST.get('strike_premium')),
                total_contracts=quantity
            )
            long_put.save()

            protective_put = ProtectivePut(
                portfolio=portfolio,
                ticker=ticker,
                stock_position=stock,
                long_put=long_put,
                quantity=quantity,
            )
            protective_put.save()

        elif strategy == 'collar':
            long_put = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='PUT',
                long_or_short='LONG',
                expiration_date=request.POST.get('expiration_date'),
                strike_price=decimal.Decimal(request.POST.get('strike_price')),
                average_price=decimal.Decimal(request.POST.get('strike_premium')),
                total_contracts=quantity
            )
            short_call = OptionPosition(
                portfolio=portfolio,
                ticker=ticker,
                call_or_put='CALL',
                long_or_short='SHORT',
                expiration_date=request.POST.get('short_call_expiration_date'),
                strike_price=decimal.Decimal(request.POST.get('short_call_strike_price')),
                average_price=decimal.Decimal(request.POST.get('short_call_strike_premium')),
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
                quantity=quantity,
            )
            collar.save()

    return redirect(reverse('view_portfolio', args=[portfolio_id]))