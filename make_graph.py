import plotly
import plotly.graph_objs as go

plotly.offline.init_notebook_mode()

def make_graph(set_dict):

    data = []
    frames = {}

    scale = 3

    mk_frame = lambda name,x,y,z : dict(x=x,
                        y=y,
                        mode='markers',
                        name=k,
                        marker=dict(size=z*scale))

    for k in set_dict.keys():

        ele = set_dict[k]

        x = ele[0]
        y = ele[1]
        z = ele[2]

        lengths = ele[3]

        trace = go.Scatter(
            x = x,
            y = y,
            name = k,
            text = ['Magnitude:{}'.format(z[i]) for i in range(len(x))],
            mode = 'markers',
            marker = dict(
                size = [i * scale for i in z],
                #color = 'rgba(152, 0, 0, .8)',
                line = dict(
                    width = 1,
                    color = 'rgb(0, 0, 0)'
                )
            )
        )

        data += [trace]

        for i in range(len(x)):
            if i not in frames:
                frames[i] = []
            frames[i] += [mk_frame(k, x[i],y[i],z[i])]

    frames = [{'data':i} for i in frames.values()]


    layout = dict(title = 'Wikipedia Sentiment Analysis',
                  yaxis = dict(zeroline = False),
                  xaxis = dict(zeroline = False),
                  annotations=[
                    dict(
                        x='2005-06-01',
                        y=0.5,
                        xref='x',
                        yref='y',
                        text='Positive sentiment, small confidence',
                        showarrow=True,
                        arrowhead=0,
                        ax=0,
                        ay=-40),
                    dict(
                        x='2017-07-01',
                        y=-0.1,
                        xref='x',
                        yref='y',
                        text='Negative sentiment, large confidence',
                        showarrow=True,
                        arrowhead=0,
                        ax=0,
                        ay=-40),
                    dict(
                        x='2011-05-01',
                        y=0.4,
                        xref='x',
                        yref='y',
                        text='Google Sentiment Analysis of the summary paragraph of Donald Trump\'s Wikipedia page, May 2011.',
                        showarrow=True,
                        arrowhead=0,
                        ax=0,
                        ay=-40)
                    ]
                )


    fig = dict(data=data, layout=layout)
    plotly.offline.plot(fig, filename='styled-scatter')
