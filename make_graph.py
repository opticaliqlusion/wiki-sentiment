import plotly
import plotly.graph_objs as go

import random
import csv


def make_graph(set_dict):

    data = []
    scale = 3

    for k in set_dict.keys():
        
        ele = set_dict[k]
    
        trace = go.Scatter(
            x = ele[0],
            y = ele[1],
            name = k,
            mode = 'markers',
            marker = dict(
                size = [i * scale for i in ele[2]],
                #color = 'rgba(152, 0, 0, .8)',
                line = dict(
                    width = 1,
                    color = 'rgb(0, 0, 0)'
                )
            )
        )

        data += [trace]

    layout = dict(title = 'Wikipedia Sentiment Analysis',
                  yaxis = dict(zeroline = False),
                  xaxis = dict(zeroline = False)
                 )

    fig = dict(data=data, layout=layout)
    plotly.offline.plot(fig, filename='styled-scatter')
