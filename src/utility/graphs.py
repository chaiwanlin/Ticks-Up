import plotly.io as pio
pio.templates.default = "none"
import plotly.express as px
import chart_studio.plotly as py
import numpy as np
import math
import matplotlib.figure
import matplotlib.pyplot as plt
import matplotlib.spines as sp

def p_and_l(lower_bound, upper_bound, delta, profit, loss, capped_profit, capped_loss, synthetic_split = False, synthetic_net = 0):
    ax1 = plt.subplot(1,1,1)

    # ax1.spines['left'].set_position(('data', 0))
    ax1.spines['bottom'].set_position(('data', 0))
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

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
                min_range = upper_bound * 0.7
                max_range = upper_bound * 1.3   
                x = [min_range, upper_bound, max_range]
                y = [loss, profit, profit]
        else:
            if capped_loss:
                min_range = lower_bound * 0.7
                max_range = lower_bound * 1.3   
                x = [min_range, lower_bound, max_range]
                y = [loss, loss, profit]
            else:
                if synthetic_split == True: 
                    min_range = lower_bound - 0.3 * mid
                    max_range = upper_bound + 0.3 * mid
                    x = [lower_bound * 0.8, lower_bound, upper_bound, upper_bound * 1.2]
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
                min_range = lower_bound * 0.7
                max_range = lower_bound * 1.3      
                x = [min_range, lower_bound, max_range]
                y = [profit, profit, loss]
        else:
            if capped_loss:
                min_range = upper_bound * 0.7
                max_range = upper_bound * 1.3     
                x = [min_range, lower_bound, max_range]
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
        title_text="hehexd",
        height=500,
        width=800,
    )
    pio.write_html(fig, file='hello_world.html', auto_open=True)
    # url = py.plot(fig, filename='graph', auto_open=True)
    # print(url)
    fig.show()

    # plt.hlines(y = 0 ,xmin = min_range, xmax = max_range)
    # plt.plot(x,y)
    # plt.savefig("graph.jpeg")
    # plt.show()

    return None

# x = [2,5,7,10]
# y = [-3,-3,7,7]

# fig = plt.figure()

# ax1 = plt.subplot(1,1,1)

# # ax1.spines['left'].set_position(('data', 0))
# ax1.spines['bottom'].set_position(('data', 0))
# ax1.spines['top'].set_visible(False)
# ax1.spines['right'].set_visible(False)

# # plt.hlines(y=0,xmin=0, xmax= 10)
# plt.plot(x,y)
# plt.show()

p_and_l(5, 10 , 1, 20, 10, False, False, True, 10)