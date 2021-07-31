import plotly.io as pio
pio.templates.default = "none"
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import chart_studio.plotly as py
import numpy as np
import math
import matplotlib.pyplot as plt
import matplotlib.spines as sp
import os
from pathlib import Path

def p_and_l(name, lower_bound, upper_bound, delta, profit, loss, capped_profit, capped_loss, full_html = True, synthetic_split = False, synthetic_net = 0):
    loss = -loss
    mid = (upper_bound + lower_bound)/2
    min_range = -math.inf
    max_range = math.inf

    if delta > 0:
        if capped_profit:
            if capped_loss:
                min_range = lower_bound - 0.3 * mid
                max_range = upper_bound + 0.3 * mid                
                x = [min_range, lower_bound, upper_bound, max_range]
                y = [loss, loss, profit, profit]
            else:
                min_range = lower_bound
                max_range = upper_bound * 1.3   
                x = [min_range, upper_bound, max_range]
                y = [loss, profit, profit]
        else:
            if capped_loss:
                min_range = lower_bound * 0.7
                max_range = upper_bound   
                x = [min_range, lower_bound, max_range]
                y = [loss, loss, profit]
            else:
                if synthetic_split == True: 
                    min_range = lower_bound - 0.3 * mid
                    max_range = upper_bound + 0.3 * mid
                    x = [min_range, lower_bound, upper_bound, max_range]
                    y = [loss, synthetic_net, synthetic_net, profit]
                else:
                    min_range = lower_bound
                    max_range = upper_bound
                    x = [lower_bound, upper_bound]
                    y = [loss, profit]
    elif delta < 0:
        if capped_profit:
            if capped_loss:
                min_range = lower_bound - 0.3 * mid
                max_range = upper_bound + 0.3 * mid
                x = [min_range, lower_bound, upper_bound, max_range]
                y = [profit, profit, loss, loss]
            else:
                min_range = lower_bound
                max_range = upper_bound * 1.3      
                x = [min_range, upper_bound, max_range]
                y = [profit, profit, loss]
        else:
            if capped_loss:
                min_range = lower_bound
                max_range = upper_bound * 1.3     
                x = [min_range, upper_bound, max_range]
                y = [profit, loss, loss]
            else:
                if synthetic_split == True: 
                    min_range = lower_bound - 0.3 * mid
                    max_range = upper_bound + 0.3 * mid
                    x = [min_range, lower_bound, upper_bound, max_range]
                    y = [profit, synthetic_net, synthetic_net, loss]
                else:
                    min_range = lower_bound
                    max_range = upper_bound
                    x = [lower_bound, upper_bound]
                    y = [profit, loss]
    
    fig = px.line(x=x, y=y, labels={'x':'price', 'y':'value'})
    fig.update_layout(
        showlegend=False,
        title_text=name,
        height=500,
        width=800,
    )
    PATH_jpeg = os.path.join(Path(__file__).resolve().parent.parent.parent,
                             "./ticks_up/static/graphs/{name}.jpeg".format(name=name))
    PATH_html = os.path.join(Path(__file__).resolve().parent.parent.parent,
                             "./ticks_up/static/graphs/{name}.html".format(name=name))
    fig.write_image(PATH_jpeg)
    pio.write_html(fig, file=PATH_html, full_html=full_html, auto_open=False)
    # url = py.plot(fig, filename='graph', auto_open=True)
    # print(url)
    # fig.show()

    # ax1 = plt.subplot(1,1,1)

    # #ax1.spines['left'].set_position(('data', 0)) this line actually should be commented out
    # ax1.spines['bottom'].set_position(('data', 0))
    # ax1.spines['top'].set_visible(False)
    # ax1.spines['right'].set_visible(False)

    # plt.hlines(y = 0 ,xmin = min_range, xmax = max_range)
    # plt.plot(x, y)
    # plt.savefig("graph.jpeg")
    # plt.show()
    return fig.to_html(full_html=False, default_height=300, default_width=500)


def spread_graph(max, min, max_profit, max_loss):
    ends_length = (max - min) / 2
    start = math.ceil(min - ends_length)
    end = math.floor(max + ends_length)

    intervals = (end - start) * 10
    x = np.linspace(start, end, intervals + 1)
    y = []
    for price in x:
        if price <= min:
            y.append(max_profit)
        elif price >= max:
            y.append(max_loss)
        else:
            y.append(max_profit + (((max_profit - max_loss) / (min - max)) * (price - min)))


    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, name='P&L'))
    fig.update_layout(hovermode='x unified')
    fig.show()


def draw_graph(**kwargs):
    price_limit = kwargs['price_limit']
    coordinate_lists = kwargs['coordinate_lists']
    intervals = int(price_limit * 10) + 1

    fig = go.Figure()

    for coordinate_list in coordinate_lists:
        x_list = np.linspace(0, price_limit, intervals)
        y_list = []
        for x in x_list:
            y_list.append(get_y(round(x, 2), coordinate_list['coordinates']))

        fig.add_trace(go.Scatter(x=x_list, y=y_list, name=coordinate_list['name']))

    fig.update_layout(
        hovermode='x unified',
        dragmode="pan",
        xaxis_title="price",
        yaxis_title="p&l",
        legend_title="Strategies (click on each to show/hide):",
    )

    config = {'scrollZoom': True,
              }

    # fig.show(config=config)
    return fig.to_html(config=config, full_html=False, default_height=600, default_width=1200)


def get_y(x, coordinate_list):
    for i in range(0, len(coordinate_list)):
        if x == coordinate_list[i][0]:
            return coordinate_list[i][1]

        elif i == len(coordinate_list) - 1:
            if coordinate_list[i][0] == coordinate_list[i - 1][0]:
                return coordinate_list[i][1]

            gradient = (coordinate_list[i][1] - coordinate_list[i - 1][1]) / (
                    coordinate_list[i][0] - coordinate_list[i - 1][0])
            return coordinate_list[i - 1][1] + (gradient * (x - coordinate_list[i - 1][0]))

        elif (coordinate_list[i][0] < x < coordinate_list[i + 1][0]) or i == 0 and x <= coordinate_list[i][0]:
            gradient = (coordinate_list[i][1] - coordinate_list[i + 1][1]) / (
                        coordinate_list[i][0] - coordinate_list[i + 1][0])
            return coordinate_list[i][1] + (gradient * (x - coordinate_list[i][0]))
    return 0


def make_pie(dict, title=""):
    labels = []
    values = []
    for ticker, perc in dict.items():
        labels.append(ticker)
        values.append(perc)

    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_traces(hoverinfo='label+percent')
    fig.update_layout(title=title)
    return fig.to_html(full_html=False, default_height=300, default_width=600)


def peak_graph(name, lower_bound, upper_bound, short_call, short_put, long_call, long_put):
    x = [long_put, short_put, short_call, long_call]
    y = [lower_bound, upper_bound, upper_bound, lower_bound]
    fig = px.line(x=x, y=y, labels={'x': 'price', 'y': 'value'})
    fig.update_layout(
        showlegend=False,
        title_text=name,
        height=500,
        width=800,
    )
    arrow_length = short_put - long_put
    fig.add_annotation(
        x=long_put - arrow_length,  # arrows' head
        y=lower_bound,  # arrows' head
        ax=long_put,  # arrows' tail
        ay=lower_bound,  # arrows' tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        text='',  # if you want only the arrow
        showarrow=True,
        arrowhead=1,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='#1F77B4'
    )
    fig.add_annotation(
        x=long_call + arrow_length,  # arrows' head
        y=lower_bound,  # arrows' head
        ax=long_call,  # arrows' tail
        ay=lower_bound,  # arrows' tail
        xref='x',
        yref='y',
        axref='x',
        ayref='y',
        text='',  # if you want only the arrow
        showarrow=True,
        arrowhead=1,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor='#1F77B4'
    )
    fig.show()
    return fig.to_html(full_html=False, default_height=300, default_width=500)


# peak_graph("yeet", -2, 2, 20, 15, 25, 10)
# spread_graph(10, 5, 10, -10)
# draw_graph(price_limit=200, coordinate_lists=[{'name': 'max_gain', 'coordinates': [(0, -10), (25, -10), (75, 10), (100, 10)]},
#                                               {'name': 'max_gain', 'coordinates': [(0, -5), (40, -5), (60, 5), (100, 5)]},
#                                               {'name': 'iron_condor', 'coordinates': [(0, -10), (25, -10), (40, 15), (60, 15), (75, -10), (100, -10)]}])
draw_graph(price_limit=0, coordinate_lists=[])