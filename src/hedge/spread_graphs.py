import utility.graphs as gp

def bull_spread(name, lower_bound, upper_bound, profit, loss, full_html = True):
    return gp.p_and_l(name, lower_bound, upper_bound, 1, profit, loss, True, True, full_html = full_html)

def bear_spread(name, lower_bound, upper_bound, profit, loss, full_html = True):
    return gp.p_and_l(name, lower_bound, upper_bound, -1, profit, loss, True, True, full_html = full_html)

# def collar(lower_bound, upper_bound, profit, loss, full_html = True):
#     gp.p_and_l(lower_bound, upper_bound, 1, profit, loss, True, True, full_html = full_html)
    
def hedge_stock(name, lower_bound, upper_bound, profit, loss, full_html = True):
    return gp.p_and_l(name, lower_bound, upper_bound, 1, profit, loss, False, True, full_html = full_html)

def iron_condor_graph(name, lower_bound, upper_bound, short_call, short_put, long_call, long_put):
    return gp.peak_graph(name, lower_bound, upper_bound, short_call, short_put, long_call, long_put)

