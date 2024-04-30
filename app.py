#Import dependencies
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from dash import Dash, dcc, html, Input, Output, callback, dash_table, State
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import random
from PIL import Image


stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css'] # load the CSS stylesheet

app = Dash(__name__, external_stylesheets=stylesheets) # initialize the app
server = app.server

# import data
df = pd.read_csv("data.csv")

#Round win/loss % to 2 decimal places
df["win_loss_perc"] = df["win_loss_perc"].round(2)

# rename the columns
df.rename(columns={
    "year": "Season Year",
    "team": "Team Name",
    "wins": "Games Won",
    "losses": "Games Lost",
    "win_loss_perc": "Win/Loss Percentage",
    "points": "Points For",
    "points_opp": "Points Against",
    "points_diff": "Point Differential",
    "mov": "Average Margin of Victory (or Defeat)",
    "g": "Games Played",
    "total_yards": "Offensive Yards Gained",
    "plays_offense": "Offensive Plays Ran",
    "yds_per_play_offense": "Yards Per Play Offense",
    "turnovers": "Team Turnovers Lost",
    "fumbles_lost": "Team Fumbles Lost",
    "first_down": "First Downs Gained",
    "pass_cmp": "Passes Completed",
    "pass_att": "Pass Attempts",
    "pass_yds": "Passing Yards",
    "pass_td": "Passing Touchdowns",
    "pass_int": "Interceptions Thrown",
    "pass_net_yds_per_att": "Net Yards Gained Per Pass Attempt",
    "pass_fd": "Passing First Downs Gained",
    "rush_att": "Rushing Attempts",
    "rush_yds": "Rushing Yards",
    "rush_td": "Rushing Touchdowns",
    "rush_yds_per_att": "Rushing Yards Per Attempt",
    "rush_fd": "Rushing First Downs",
    "penalties": "Penalties Committed",
    "penalties_yds": "Penalty Yards Committed",
    "pen_fd": "First Downs by Penalty",
    "score_pct": "Percentage of Drives Ending in Score",
    "turnover_pct": "Percentage of Drives Ending in Turnover",
    "exp_pts_tot": "Expected Points Contributed by Offense",
    "ties": "Ties",
    "conference": "NFL Conference",
    "division": "NFL Division"
},inplace = True)

desired_columns = ["Team Name", "Games Won", "Games Lost","Win/Loss Percentage", 
                   "Points For", "Points Against", "Point Differential"]

# create datatable
dtable = dash_table.DataTable(
    columns=[{"name": i, "id": i} for i in desired_columns],
    data=df.sort_values(by="Games Won", ascending=False).to_dict('records'),  # Sort data by 'Games Won' column
    sort_action="native",
    page_size=16,
    style_data_conditional=[
        {
            'if': {'row_index': 'odd'},  # Apply style to odd rows
            'backgroundColor': 'rgb(240, 240, 240)',  # Set background color to light grey
            'color': 'black',  # Set text color to black
        },
        {
            'if': {'row_index': 'even'},  # Apply style to even rows
            'backgroundColor': 'white',  # Set background color to white
            'color': 'black',  # Set text color to black
        },
        #{
        #    'if': {'filter_query': '{Games Won} >= 10'},  # Apply style to rows with Games Won >= 14
        #    'backgroundColor': 'green',  # Set background color to green
        #    'color': 'white',  # Set text color to black
        #},
    ],
    style_cell={'whiteSpace': 'normal', 'overflow': 'hidden', 'textOverflow': 'ellipsis', # Wrap text if needed
        'backgroundColor': '#013369',  # Set cell background color
        'color': 'black' # Set cell text color to white
        },
    style_header={'whiteSpace': 'normal', 'overflow': 'hidden', 'textOverflow': 'ellipsis',
        'backgroundColor': '#013369',  # Set header background color
        'fontWeight': 'bold',  # Make header text bold
        'color': 'white',  # Set header text color to white  
        },
    style_table={'overflowX': 'auto','backgroundColor': '#013369'},  # Set background color
)

unique_conferences = df["NFL Conference"].unique()
conference_options = [{'label': conference, 'value': conference} for conference in unique_conferences]
conference_options.append({'label': 'All', 'value': 'All'})  # Manually add 'All' option


#---------------------------------------------------------------------------------------#
#--------------------------------------App Layout---------------------------------------#
#---------------------------------------------------------------------------------------#

# layout of the app
app.layout = html.Div(style={'backgroundColor': '#f2f2f2'},children = [

 html.Div([
       html.H4("Home", style={'color': 'white', 'margin-left': '10px','font-weight': 'bold','font-size': '18px'}),
    ], style={'background-color': '#013369', 'height': '40px', 'display': 'flex','align-items': 'center'}),
    
    html.Div([
        html.H1("National Football League Team Analysis",
                style={'text-align': 'center', 'margin-top': '5px', 'margin-bottom': '5px','font-size': '24px'}),  # Title
        html.H2("A Visualization of Historical Data (2003-2023)",
                style={'text-align': 'center', 'margin-top': '5px', 'margin-bottom': '5px','font-size': '18px','font-style': 'italic'}),  # Title 2
    ]),
    
    #html.Div([],
            # style={'height': '20px'}),  # Add space between description and slider/dropdown


html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'border': '1px solid #ccc'}, children=[
    html.Div(style={'display': 'flex'}, children=[
        # Radio button and division dropdown
        html.Div([
            html.Label('Select NFL Conference:'),
            dcc.RadioItems(
                options=conference_options,
                id='conference-radio',
                value = 'All'
            ),
            html.Label('Select NFL Division:'),
            dcc.Dropdown(id='division-dropdown',placeholder="Select NFL Division",
                         #style={'backgroundColor': '#D50A0A', 'color': 'black'},
                         )
        ], style={'width': '30%', 'marginRight': '20px'}),
        
        # Slider and team dropdown
        html.Div([
            html.Label('Select Year to Analyze:'),
            dcc.Slider(
                min=df['Season Year'].min(),
                max=df['Season Year'].max(),
                step=1,
                value=df['Season Year'].max(),
                marks={str(year): str(year) for year in df['Season Year'].unique() if year % 2 == 0},
                tooltip={"placement": "bottom", "always_visible": True},
                id='year-slider',
            )
        ], style={'width': '30%', 'marginRight': '20px'}),
        
        # Team dropdown, X-axis dropdown, and Y-axis dropdown
        html.Div([
            html.Label('Select NFL Teams to Analyze:'),
            dcc.Dropdown(
                id='team-dropdown',
                options=[{'label': team, 'value': team} for team in df['Team Name'].unique()],
                placeholder="Select NFL Teams to Analyze",
                value=random.sample(list(df["Team Name"].unique()),8),
                multi=True,
                #style={'height': 'auto','backgroundColor': '#D50A0A', 'color': 'black'},
            ),
            html.Label('Select X-Axis Metric (Only Modifies Graph):'),
            dcc.Dropdown(
                id='x-axis-dropdown',
                options=[{'label': col, 'value': col} for col in df.columns[3:]],
                placeholder = "Select X-Axis Metric",
                value=df.columns[19],
                #style={'backgroundColor': '#D50A0A', 'color': 'black'},
            ),
            html.Label('Select Y-Axis Metric (Only Modifies Graph):'),
            dcc.Dropdown(
                id='y-axis-dropdown',
                options=[{'label': col, 'value': col} for col in df.columns[3:]],
                placeholder = "Select Y-Axis Metric:",
                value=df.columns[25],
                #style={'backgroundColor': '#D50A0A', 'color': 'black'},
            )
        ], style={'width': '30%', 'marginRight': '20px'})
    ]),
]),


    html.Br(),
    
html.Div(id='table-title', style={'textAlign': 'left', 'font-weight': 'bold'}),
html.Div(style={'display': 'flex'}, children=[
    html.Div(
        html.Div(dtable,style={'padding': '10px', 'border': '1px solid #ccc', 'backgroundColor': 'white'}), 
    style={'flex': '1', 'width': '45%', 'marginRight': '10px'}),
    html.Div(dcc.Graph(id='graph-with-slider'), style={'flex': '1', 'width': '45%', 'marginLeft': '10px'}),
])
 

])


#---------------------------------------------------------------------------------------#
#-----------------------------------Radio Button Callback-------------------------------#
#---------------------------------------------------------------------------------------#

@callback(
    Output('division-dropdown', 'options'),
    Input('conference-radio', 'value'))
def set_category_options(selected_category):
    if selected_category == 'All':
        # Provide options for all divisions across both conferences
        subcategories = df["NFL Division"].unique()
    else:
        # Filter divisions based on the selected conference
        filtered_df = df[df["NFL Conference"] == selected_category]
        subcategories = filtered_df["NFL Division"].unique()

    subcategory_options = [{'label':subcategory, 'value':subcategory} for subcategory in subcategories]
    return subcategory_options


#--------------------------------------------------------------------------------------------#
#--------------------------------------Graph Callback----------------------------------------#
#--------------------------------Code for Icons on Graph-------------------------------------#
#------------https://community.plotly.com/t/put-images-inside-bubbles/41364/2----------------#
#https://github.com/tbryan2/NFL-Python-Team-Logo-Viz/blob/main/Team-Logo-Visualizations.ipynb#
#--------------------------------------------------------------------------------------------#

# define callbacks
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value'),
     Input('team-dropdown','value'),
     Input('x-axis-dropdown','value'),
     Input('y-axis-dropdown','value'),
     Input('conference-radio', 'value'),
     Input('division-dropdown', 'value')])

def update_figure(selected_year, selected_teams,x_axis,y_axis,selected_conference,selected_division):
    if None in [selected_year, selected_teams, x_axis, y_axis]:
        # Return a default or empty figure if any input value is None
        return {
            'data': [],
            'layout': {}
        }
    
    filtered_df = df[df["Season Year"] == selected_year]

    # Filter by selected teams
    if selected_teams:
        filtered_df = filtered_df[filtered_df['Team Name'].isin(selected_teams)]

    # Filter by selected conference
    if selected_conference is not None and selected_conference != 'All':
        filtered_df = filtered_df[filtered_df['NFL Conference'] == selected_conference]


    # Filter by selected division
    if selected_division:
        filtered_df = filtered_df[filtered_df['NFL Division'] == selected_division]

    fig = px.scatter(filtered_df, x=x_axis, y=y_axis,
                     hover_name="Team Name",
                     )

    fig.update_traces(marker_color="rgba(0,0,0,0)")

    title = f"{y_axis} vs {x_axis}"
    fig.update_layout(title = title, transition_duration=500)

    #Calculate median values for x and y axes
    x_median = filtered_df[x_axis].median()
    y_median = filtered_df[y_axis].median()

    # Add lines for x and y medians
    fig.add_hline(y=y_median, line_dash="dash", line_color="red", annotation_text=f"Median {x_axis}")
    fig.add_vline(x=x_median, line_dash="dash", line_color="blue", annotation_text=f"Median {y_axis}")


    # Update markers with custom images
    for i, row in filtered_df.iterrows():
        logo_path = row['Logo Path']
        if logo_path:
            fig.add_layout_image(
                dict(
                    source=Image.open(f"C:/Users/ghisv/OneDrive/Documents/VS Code/DS4002/{logo_path}"),
                    xref="x",
                    yref="y",
                    xanchor="center",
                    yanchor="middle",
                    x=row[x_axis],
                    y=row[y_axis],
                    #x=filtered_df.loc[i, x_axis],
                    #y=filtered_df.loc[i, y_axis],
                    sizex=(filtered_df[x_axis].max() - filtered_df[x_axis].min())*.1,
                    sizey=(filtered_df[y_axis].max() - filtered_df[y_axis].min())*.1,
                    layer="above",
                )
            )

    return fig

#---------------------------------------------------------------------------------------#
#--------------------------------------Data Table Callback------------------------------#
#---------------------------------------------------------------------------------------#

@app.callback(
    Output(dtable, "data"), # changes data in table
    Output('table-title', 'children'),
    Input('year-slider', "value"), # based on input from range_slider
    Input('conference-radio', 'value'),
    Input('division-dropdown', 'value')
)

# function that filters table based on range slider input
def update_table(slider_value, selected_conference, selected_division): 
    if not slider_value:
        return dash.no_update

    filtered_df = df[df["Season Year"] == slider_value]

    # Filter by selected conference
    if selected_conference and selected_conference != 'All':
        filtered_df = filtered_df[filtered_df['NFL Conference'] == selected_conference]

    # Filter by selected division
    if selected_division:
        filtered_df = filtered_df[filtered_df['NFL Division'] == selected_division]

    if selected_division:
        title = f"{selected_division} standings for {slider_value} season"
    else:
        title = f"Overall standings for {slider_value} season"

    filtered_df = filtered_df.sort_values(by="Games Won", ascending=False)

    return filtered_df.to_dict("records"),title

# run the app
if __name__ == '__main__':
    app.run_server(debug=True)
