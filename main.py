from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import dash_draggable

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1(children='Application with countries', style={'textAlign': 'center'}),
    dcc.Dropdown(
        df.country.unique(),
        placeholder='Choose countries',
        id='dropdown-selection',
        persistence='local',
        multi=True),
    html.Div(children='Choose measure', style={'font-size': 18, 'padding': 5}),
    dcc.Dropdown(
        ['lifeExp', 'pop', 'gdpPercap'],
        'pop',
        id='dropdown-measure',
        persistence='local'),
    html.Div(children='Choose x for scatter', style={'font-size': 18, 'padding': 5}),
    dcc.Dropdown(
        ['lifeExp', 'pop', 'gdpPercap'],
        'pop',
        id='dropdown-axes-x',
        persistence='local'),
    html.Div(children='Choose y for scatter', style={'font-size': 18, 'padding': 5}),
    dcc.Dropdown(
        ['lifeExp', 'pop', 'gdpPercap'],
        'lifeExp',
        id='dropdown-axes-y',
        persistence='local'),
    dash_draggable.ResponsiveGridLayout([
        dcc.Graph(id='graph-content'),
        dcc.Graph(id='top-population'),
        dcc.Graph(id='scatter'),
        dcc.Graph(id='pie')
    ]),

])


@callback(
    Output('pie', 'figure'),
    Input('graph-content', 'clickData')
)
def update_scatter(point):
    if point is not None:
        value = point['points'][0]['x']
        dff = df[df.year == value].groupby(['continent'])['pop'].sum()
        return px.pie(dff, values='pop', names=dff.index)
    else:
        dff = df.groupby(['continent', 'country'])['pop'].mean().groupby('continent', axis=0).sum()
        return px.pie(dff, values='pop', names=dff.index)


@callback(
    Output('scatter', 'figure'),
    Input('dropdown-axes-x', 'value'),
    Input('dropdown-axes-y', 'value'),
    Input('dropdown-measure', 'value')
)
def update_scatter(x, y, measure):
    return px.scatter(df, x=x, y=y, size=measure)


@callback(
    Output('graph-content', 'figure'),
    Input('dropdown-selection', 'value'),
    Input('dropdown-measure', 'value')
)
def update_graph(value, measure):
    dff = df[df.country.isin(value)]
    return px.line(dff, x='year', y=measure, color='country')


@callback(
    Output('top-population', 'figure'),
    Input('dropdown-measure', 'value'),
    Input('graph-content', 'clickData')
)
def update_bar(measure, point):
    if point is not None:
        value = point['points'][0]['x']
        return px.bar(
            df[df.year == value].groupby('country')
            .mean(measure)[[measure]]
            .sort_values(measure, ascending=False)
            .head(15))
    else:
        return px.bar(
            df.groupby('country')
            .mean(measure)[[measure]]
            .sort_values(measure, ascending=False)
            .head(15))


if __name__ == '__main__':
    app.run(debug=True)
