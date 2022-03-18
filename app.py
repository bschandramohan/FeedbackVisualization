import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
# https://dash.plotly.com/dash-core-components/dropdown
from dash import Dash, dcc, html, Input, Output

from helpers import sentiment_scores, get_sentiment_scores_text

import operator

# here's the list of possible columns to choose from.
list_of_columns = ["type", "systeminfo_identifier", "accountid", "product", "assetalias", "feature", "featureversion", "appversion", "binaryrating", "realmid", "scalerating", "useragent", "updateddate", "deviceosversion", "tags", "scaleratingmax", "feedbacktext", "useridentifiers_country", "useridentifiers_language", "clienttype", "displayfeature", "displayfeedback"]

github_link = 'https://github.com/bschandramohan/DataScienceConnect'

# Set up the chart
df = pd.read_csv('data/FeedbackData_upto_03152022.csv')

# Initiate the app
external_stylesheets = ['https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = 'Product Feedback Data Visualization'

product_list = np.append("ALL", df["product"].unique())
app_list = np.append("ALL", df["assetalias"].unique())
feature_list = np.append("ALL", df["feature"].unique())

# Set up the layout
app.layout = html.Div(children=[
    # html.Br(),
    html.H1(id="page_heading"),
    html.Br(),
    html.Br(),
    html.P("Select product type here:"),
    dcc.Dropdown(
        options=product_list,
        value=product_list[0],
        id="product-options-dropdown",
        style={'width': '60%'},
    ),
    html.P("Select app type here:"),
    dcc.Dropdown(
        options=app_list,
        value=app_list[0],
        id="app-options-dropdown",
        style={'width': '60%'},
    ),
    html.P("Select feature id here:"),
    dcc.Dropdown(
        options=feature_list,
        value=feature_list[0],
        id="feature-options-dropdown",
        style={'width': '60%'},
    ),
    html.Br(),
    html.Hr(),
    html.Br(),
    html.H2('Sentiment Analysis'),
    # html.Div(id='output-div-1'),
    html.Div(id='output-div-2'),
    html.Div(id='output-div-3'),
    html.Div(id='output-div-4'),
    html.H3(id='output-div-5'),
    html.Hr(),
    html.Br(),
    html.H2('Ratings'),
    dcc.Graph(
        id='thumbs-figure',
        figure={},
        style={'align': 'center'}
    ),
    html.Br(),
    html.Hr(),
    html.Br(),
    html.H2('Weekly Ratings Distribution'),
    dcc.Graph(
        id='weekly-figure',
        figure={},
        style={'align': 'center'}
    ),
    html.Br(),
    html.A('Code on Github', href=github_link),
    html.Br(),
    html.A('Contact me on medium', href='https://bschandramohan.medium.com/'),
    html.Br(),
    ],
    id="parent_container",
)


# Purposefully not using 'State' but 'Input' to make sure data updates happen if any drop down changes and there
# is no need to press another submit button.
@app.callback(
    [Output('thumbs-figure', 'figure'),
     Output('weekly-figure', 'figure'),
     Output('page_heading', 'children'),
     # Output('output-div-1', 'children'),
     Output('output-div-2', 'children'),
     Output('output-div-3', 'children'),
     Output('output-div-4', 'children'),
     Output('output-div-5', 'children'),
     ],
    [Input('product-options-dropdown', 'value'),
     Input('app-options-dropdown', 'value'),
     Input('feature-options-dropdown', 'value')],
)
def update_figure_callback(product, app_type, feature):
    updated_heading = update_heading(product, app_type, feature)
    applicable_dataframe = get_dataframe(product, app_type, feature)
    # print(applicable_dataframe.head())
    figure = update_pie(applicable_dataframe)
    weekly_figure = update_bar(applicable_dataframe)

    # drop the empty rows in feedback text as we are not interested in them.
    # OPTION 1: here we get the series of feedback text and convert it to data frame with just that column
    # feedback_text_df = applicable_dataframe["feedbacktext"].dropna().to_frame()

    # OR
    # OPTION 2: Use original dataframe
    applicable_dataframe.dropna(subset=["feedbacktext"], inplace=True)
    applicable_dataframe["feedback-text-analysis"] = applicable_dataframe["feedbacktext"].apply(sentiment_scores)
    df1 = pd.concat([applicable_dataframe, pd.DataFrame(list(applicable_dataframe['feedback-text-analysis']))], axis=1)
    # print(df1.dtypes)

    r1, r2, r3, r4, r5 = get_sentiment_scores_text({"neg": df1["neg"].mean(),
                               "neu": df1["neu"].mean(),
                               "pos": df1["pos"].mean(),
                               "compound": df1["compound"].mean(), })

    return figure, weekly_figure, updated_heading, r2, r3, r4, r5


def update_heading(product, app_type, feature):
    if product == 'ALL' and app_type == 'ALL' and feature == 'ALL':
        return "Product Feedback Data Visualization"
    else:
        return f"Feedback Data Visualization for product={product} app={app_type} feature={feature}"


def get_dataframe(product, app_type, feature):
    if product == 'ALL':
        product_df = df
    else:
        product_df = df[df['product'] == product]

    if app_type == 'ALL':
        app_df = product_df
    else:
        app_df = product_df[product_df['assetalias'] == app_type]

    if feature == 'ALL':
        feature_df = app_df
    else:
        feature_df = app_df[app_df['feature'] == feature]

    return feature_df


def update_pie(dataframe):
    figure = px.pie(
        data_frame=dataframe,
        names='binaryrating',
        title='Feedback Data',
        width=800,
        height=600,
    )

    return figure


def update_bar(dataframe):
    # Get week (of the year) into the dataframe
    dataframe.dropna(subset=["updateddate"], inplace=True) # Is this even required, since we are doing a join
    dataframe["datetime"] = pd.to_datetime(dataframe["updateddate"])
    dataframe["week"]=dataframe["datetime"].dt.isocalendar().week
    # print(dataframe)
    # Group by week of the year and ratings
    weekly_ratings_df = pd.DataFrame(dataframe.groupby(["binaryrating", "week"])["systeminfo_identifier"].count())
    # print(weekly_ratings_df)

    list_of_figures = []
    # https://stackoverflow.com/a/65661205/207552
    week_indices = list(set(map(operator.itemgetter(0), weekly_ratings_df.index.tolist())))
    # print(week_indices)
    for week in week_indices:
        # You wouldn't believe the amount of options I tried before coming up with query and reset index to figure out index.
        # note that you cannot use loc for binary value (True, False) so query works.
        # query returns multi index, so we need to reduce that to single index. Refer to https://stackoverflow.com/a/32938276/207552
        # for details on removing index
        figure = go.Bar(
            x=weekly_ratings_df.query(f'binaryrating == {week}').reset_index(level=['binaryrating']).index,
            y=weekly_ratings_df.query(f'binaryrating == {week}')['systeminfo_identifier'],
            name=f'{week}',
        )
        list_of_figures.append(figure)
    # print(list_of_figures)

    mylayout = go.Layout(
        title='Grouped bar chart',
        xaxis=dict(title='Ratings Per Week'),  # x-axis label
        yaxis=dict(title='Counts'),  # y-axis label

    )
    figure = go.Figure(data=list_of_figures, layout=mylayout)

    return figure


# Deploy
if __name__ == '__main__':
    app.run_server(debug=True)
