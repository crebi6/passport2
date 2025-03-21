import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash
from dash import dcc, html, Input, Output, callback
import flask

# Initialize Flask server with CORS configuration
server = flask.Flask(__name__)
server.config['CORS_HEADERS'] = 'Content-Type'

@server.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# Initialize Dash app with the Flask server
app = dash.Dash(__name__, server=server)

# Load the dataset from GitHub
df = pd.read_csv("https://raw.githubusercontent.com/crebi6/passport-index/refs/heads/main/encoded-passport-power1.csv")

# Create a mapping for visa requirements to colors
requirement_colors = {
    'visa_free': '#2ca25f',           # Green - easiest access
    'visa_on_arrival': '#99d8c9',     # Light green
    'electronic_visa': '#f1b6da',     # Pink
    'visa_required': '#d73027'        # Red - most restricted
}

# Add any missing requirement types from your dataset
unique_requirements = df['requirement'].unique()
for req in unique_requirements:
    if req not in requirement_colors:
        requirement_colors[req] = '#808080'  # Default gray for any other categories

# App layout
app.layout = html.Div([
    html.H1("Passport Power Index - Interactive Map", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Select Origin Country (Passport):"),
        dcc.Dropdown(
            id='origin-dropdown',
            options=[{'label': country, 'value': country} for country in sorted(df['origin'].unique())],
            value='Afghanistan'  # Default value
        )
    ], style={'width': '300px', 'margin': '20px auto'}),
    
    dcc.Graph(id='visa-map'),
    
    html.Div([
        html.Div([
            html.H3("Visa Requirements Distribution", style={'textAlign': 'center'}),
            dcc.Graph(id='requirement-pie')
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),
        
        html.Div([
            html.H3("Passport Power Metrics", style={'textAlign': 'center'}),
            html.Div(id='passport-stats', style={'padding': '20px'})
        ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'})
    ]),
    
    html.Div([
        html.H3("Countries List by Requirement Type", style={'textAlign': 'center'}),
        html.Div(id='countries-list')
    ], style={'margin-top': '30px'})
])

@app.callback(
    [Output('visa-map', 'figure'),
     Output('requirement-pie', 'figure'),
     Output('passport-stats', 'children'),
     Output('countries-list', 'children')],
    [Input('origin-dropdown', 'value')]
)
def update_output(selected_country):
    # Filter data for the selected origin country
    filtered_data = df[df['origin'] == selected_country]
    
    # Create the world map
    fig_map = px.choropleth(
        filtered_data,
        locations='destination',
        locationmode='country names',
        color='requirement',
        color_discrete_map=requirement_colors,
        title=f"Visa Requirements for {selected_country} Passport Holders",
        hover_name='destination',
        hover_data=['requirement']
    )
    
    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='natural earth'
        ),
        height=600,
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    
    # Create pie chart for requirements breakdown
    requirement_counts = filtered_data['requirement'].value_counts().reset_index()
    requirement_counts.columns = ['requirement', 'count']
    
    fig_pie = px.pie(
        requirement_counts, 
        values='count', 
        names='requirement',
        color='requirement',
        color_discrete_map=requirement_colors,
        title=f"Visa Requirement Distribution"
    )
    
    fig_pie.update_traces(textinfo='percent+label')
    
    # Calculate passport power metrics
    total_countries = len(filtered_data)
    visa_free_count = len(filtered_data[filtered_data['requirement'] == 'visa_free'])
    visa_on_arrival_count = len(filtered_data[filtered_data['requirement'] == 'visa_on_arrival'])
    e_visa_count = len(filtered_data[filtered_data['requirement'].str.contains('electronic', case=False, na=False)])
    
    # Passport power score (example calculation - can be customized)
    power_score = visa_free_count + (0.7 * visa_on_arrival_count) + (0.5 * e_visa_count)
    
    passport_stats = html.Div([
        html.Div([
            html.H4(f"Visa-Free Access:", style={'display': 'inline-block', 'marginRight': '10px'}),
            html.H4(f"{visa_free_count} countries ({visa_free_count/total_countries*100:.1f}%)", 
                   style={'display': 'inline-block', 'color': requirement_colors.get('visa_free')})
        ]),
        html.Div([
            html.H4(f"Visa on Arrival:", style={'display': 'inline-block', 'marginRight': '10px'}),
            html.H4(f"{visa_on_arrival_count} countries ({visa_on_arrival_count/total_countries*100:.1f}%)", 
                   style={'display': 'inline-block', 'color': requirement_colors.get('visa_on_arrival')})
        ]),
        html.Div([
            html.H4(f"Electronic Visa:", style={'display': 'inline-block', 'marginRight': '10px'}),
            html.H4(f"{e_visa_count} countries ({e_visa_count/total_countries*100:.1f}%)", 
                   style={'display': 'inline-block', 'color': requirement_colors.get('electronic_visa')})
        ]),
        html.Hr(),
        html.Div([
            html.H3(f"Passport Power Score: {power_score:.1f}", style={'textAlign': 'center', 'fontWeight': 'bold'})
        ])
    ])
    
    # Create requirements list by category
    categories = {}
    for req in requirement_counts['requirement']:
        countries = filtered_data[filtered_data['requirement'] == req]['destination'].tolist()
        categories[req] = countries
    
    list_components = []
    for req, countries in categories.items():
        color = requirement_colors.get(req, "#000000")
        list_components.append(
            html.Div([
                html.H4(f"{req.replace('_', ' ').title()} ({len(countries)})", 
                       style={'backgroundColor': color, 'color': 'white', 'padding': '10px'}),
                html.Ul([html.Li(country) for country in sorted(countries)], 
                       style={'columnCount': '3', 'columnGap': '20px'})
            ], style={'marginBottom': '20px'})
        )
    
    return fig_map, fig_pie, passport_stats, list_components

# Run the app
# Replace the entire if __name__ block with:
if __name__ == '__main__':
    app.run_server(debug=True, port=int(os.environ.get('PORT', 8050)))