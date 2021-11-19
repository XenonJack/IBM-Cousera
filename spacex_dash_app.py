# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout

launch_sites = []
launch_sites.append({'label': 'All Sites', 'value': 'All Sites'})
for item in spacex_df["Launch Site"].value_counts().index:
    launch_sites.append({'label': item, 'value': item})
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                    options=launch_sites,
                                    placeholder= 'Select a Launch Site here',
                                    value='ALL',
                                    searchable=True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider', min=min_payload, max=max_payload, step=None, dots=True,
                                                marks={0:'0', 1000:'1000', 2000:'2000', 3000:'3000', 4000:'4000', 5000:'5000',
                                                       6000:'6000', 7000:'7000', 8000:'8000', 9000:'9000', 
                                                       max_payload:str(max_payload)},
                                                value=[0, max_payload]),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback( Output(component_id='success-pie-chart', component_property='figure'),
               Input(component_id='site-dropdown', component_property='value')
) 
def select(input_):
    if input_ == 'All Sites':
        new_df = spacex_df.groupby(['Launch Site'])["class"].sum().to_frame()
        new_df = new_df.reset_index()
        fig = px.pie(new_df, values='class', names='Launch Site', title='Total Success Launches by Site')
    else:
        new_df = spacex_df[spacex_df["Launch Site"] == input_]["class"].value_counts().to_frame()
        new_df["name"] = ["Failure", "Success"]
        fig = px.pie(new_df, values='class', names='name', title='Total Success Launches for ' + input_)
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output('success-payload-scatter-chart', 'figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value'),
              )
def get_scatterplot(site, payload):
    if site=='All Sites':
        query = '`Payload Mass (kg)` >= {0} and `Payload Mass (kg)` <= {1}'.format(payload[0], payload[1])
        data_scatter = spacex_df.query(query)
        scatter_fig = px.scatter(data_scatter, x='Payload Mass (kg)', y='class', color='Booster Version') 
        return scatter_fig
    else:
        query = '`Payload Mass (kg)` >= {0} and `Payload Mass (kg)` <= {1} and `Launch Site` == "{2}"'.format(
            payload[0], payload[1], site)
        data_scatter = spacex_df.query(query)
        scatter_fig = px.scatter(data_scatter, x='Payload Mass (kg)', y='class',  color='Booster Version') 
        return scatter_fig

# Run the app
if __name__ == '__main__':
    app.run_server()
