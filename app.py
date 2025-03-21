import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html, Input, Output

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

# Create a dash application
app = dash.Dash(__name__, meta_tags=[
    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
])
server = app.server  # This is needed for deployment on services like Render

# Set the title that appears in the browser tab
app.title = "Passport Power Index"

# Improved layout with better styling
app.layout = html.Div([
    html.Div([
        html.H1("Passport Power Index", className="header-title"),
        html.P("Explore visa requirements for travelers around the world", className="header-description")
    ], className="header"),
    
    html.Div([
        html.Div([
            html.Label("Select Origin Country (Passport):", className="dropdown-label"),
            dcc.Dropdown(
                id='origin-dropdown',
                options=[{'label': country, 'value': country} for country in sorted(df['origin'].unique())],
                value='United States',  # Default value
                clearable=False,
                className="dropdown"
            )
        ], className="dropdown-container")
    ], className="control-row"),
    
    html.Div([
        dcc.Graph(
            id='visa-map',
            config={'displayModeBar': True, 'scrollZoom': True},
            className="map-container"
        )
    ], className="map-row"),
    
    html.Div([
        html.Div([
            html.H3("Visa Requirements Distribution", className="section-heading"),
            dcc.Graph(id='requirement-pie', className="chart")
        ], className="chart-container"),
        
        html.Div([
            html.H3("Passport Power Metrics", className="section-heading"),
            html.Div(id='passport-stats', className="stats-container")
        ], className="stats-box")
    ], className="data-row"),
    
    html.Div([
        html.H3("Countries List by Requirement Type", className="section-heading"),
        html.Div(id='countries-list', className="countries-container")
    ], className="countries-row"),
    
    html.Footer([
        html.P(["Data Source: Passport Index | Created with ❤️ using", 
                html.A("Dash by Plotly", href="https://plotly.com/dash/", target="_blank")
        ]),
        html.P("© 2025 Samuel Musyoka")
    ], className="footer")
], className="app-container")

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
    
    # Create the world map with improved styling
    fig_map = px.choropleth(
        filtered_data,
        locations='destination',
        locationmode='country names',
        color='requirement',
        color_discrete_map=requirement_colors,
        title=f"Visa Requirements for {selected_country} Passport Holders",
        hover_name='destination',
        hover_data=['requirement'],
        projection="natural earth"
    )
    
    fig_map.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            showcountries=True,
            countrycolor="#c7c7c7",
            coastlinecolor="#c7c7c7",
            projection_type='natural earth',
            landcolor="#f5f5f5",
            oceancolor="#deebf7"
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=550,
        margin={"r":10,"t":30,"l":10,"b":10},
        legend=dict(
            title="Visa Requirement",
            orientation="h",
            y=-0.1,
            yanchor="top"
        ),
        font=dict(family="Arial, sans-serif")
    )
    
    # Create pie chart for requirements breakdown with better styling
    requirement_counts = filtered_data['requirement'].value_counts().reset_index()
    requirement_counts.columns = ['requirement', 'count']
    
    # Capitalize and format requirement names for better display
    requirement_counts['display_name'] = requirement_counts['requirement'].apply(
        lambda x: x.replace('_', ' ').title()
    )
    
    fig_pie = px.pie(
        requirement_counts, 
        values='count', 
        names='display_name',
        color='requirement',
        color_discrete_map=requirement_colors,
        title=f"Visa Requirement Distribution",
        hole=0.4
    )
    
    fig_pie.update_traces(
        textinfo='percent+label',
        textposition='outside',
        textfont=dict(size=12)
    )
    
    fig_pie.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Arial, sans-serif"),
        legend=dict(
            orientation="h",
            y=-0.1,
            yanchor="top"
        ),
        margin=dict(t=30, b=30)
    )
    
    # Calculate passport power metrics
    total_countries = len(filtered_data)
    visa_free_count = len(filtered_data[filtered_data['requirement'] == 'visa_free'])
    visa_on_arrival_count = len(filtered_data[filtered_data['requirement'] == 'visa_on_arrival'])
    e_visa_count = len(filtered_data[filtered_data['requirement'].str.contains('electronic', case=False, na=False)])
    visa_required_count = len(filtered_data[filtered_data['requirement'] == 'visa_required'])
    
    # Passport power score (example calculation - can be customized)
    power_score = visa_free_count + (0.7 * visa_on_arrival_count) + (0.5 * e_visa_count)
    
    # Improved stats display
    passport_stats = html.Div([
        html.Div([
            html.Div([
                html.Span("Visa-Free Access", className="stat-label"),
                html.Div([
                    html.Span(f"{visa_free_count}", className="stat-value"),
                    html.Span(f"({visa_free_count/total_countries*100:.1f}%)", className="stat-percentage")
                ], className="stat-numbers")
            ], className="stat-item", style={'background': 'linear-gradient(to right, white, #e5f5e0)'}),
            
            html.Div([
                html.Span("Visa on Arrival", className="stat-label"),
                html.Div([
                    html.Span(f"{visa_on_arrival_count}", className="stat-value"),
                    html.Span(f"({visa_on_arrival_count/total_countries*100:.1f}%)", className="stat-percentage")
                ], className="stat-numbers")
            ], className="stat-item", style={'background': 'linear-gradient(to right, white, #e0f3db)'}),
            
            html.Div([
                html.Span("Electronic Visa", className="stat-label"),
                html.Div([
                    html.Span(f"{e_visa_count}", className="stat-value"),
                    html.Span(f"({e_visa_count/total_countries*100:.1f}%)", className="stat-percentage")
                ], className="stat-numbers")
            ], className="stat-item", style={'background': 'linear-gradient(to right, white, #fde0dd)'}),
            
            html.Div([
                html.Span("Visa Required", className="stat-label"),
                html.Div([
                    html.Span(f"{visa_required_count}", className="stat-value"),
                    html.Span(f"({visa_required_count/total_countries*100:.1f}%)", className="stat-percentage")
                ], className="stat-numbers")
            ], className="stat-item", style={'background': 'linear-gradient(to right, white, #fee0d2)'}),
        ], className="stats-grid"),
        
        html.Div([
            html.H2(f"{power_score:.1f}", className="power-score-value"),
            html.Div("Passport Power Score", className="power-score-label")
        ], className="power-score-container")
    ])
    
    # Create requirements list by category with improved styling
    categories = {}
    for req in requirement_counts['requirement']:
        countries = filtered_data[filtered_data['requirement'] == req]['destination'].tolist()
        categories[req] = countries
    
    list_components = []
    for req, countries in categories.items():
        display_name = req.replace('_', ' ').title()
        color = requirement_colors.get(req, "#808080")
        
        list_components.append(
            html.Div([
                html.Div([
                    html.Span(f"{display_name}", className="category-label"),
                    html.Span(f"{len(countries)}", className="category-count")
                ], className="category-header", style={'backgroundColor': color}),
                
                html.Div([
                    html.Ul([
                        html.Li(country, className="country-item") 
                        for country in sorted(countries)
                    ], className="countries-list")
                ], className="countries-list-container")
            ], className="requirement-category")
        )
    
    return fig_map, fig_pie, passport_stats, list_components

# CSS for the app
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Global styles */
            * {
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            body {
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
                color: #212529;
            }
            
            /* App container */
            .app-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            /* Header section */
            .header {
                text-align: center;
                padding: 20px 0;
                margin-bottom: 20px;
                border-bottom: 1px solid #dee2e6;
            }
            
            .header-title {
                margin: 0;
                font-size: 36px;
                color: #2c3e50;
            }
            
            .header-description {
                margin-top: 10px;
                color: #6c757d;
                font-size: 18px;
            }
            
            /* Controls section */
            .control-row {
                margin-bottom: 20px;
            }
            
            .dropdown-container {
                max-width: 400px;
                margin: 0 auto;
            }
            
            .dropdown-label {
                font-weight: bold;
                margin-bottom: 5px;
                display: block;
            }
            
            .dropdown {
                width: 100%;
            }
            
            /* Map container */
            .map-row {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                padding: 15px;
                margin-bottom: 20px;
            }
            
            /* Data visualization row */
            .data-row {
                display: flex;
                flex-wrap: wrap;
                gap: 20px;
                margin-bottom: 20px;
            }
            
            .chart-container {
                flex: 1;
                min-width: 300px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                padding: 15px;
            }
            
            .stats-box {
                flex: 1;
                min-width: 300px;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                padding: 15px;
            }
            
            .section-heading {
                margin-top: 0;
                color: #2c3e50;
                font-size: 20px;
                text-align: center;
                border-bottom: 1px solid #e9ecef;
                padding-bottom: 10px;
            }
            
            /* Stats display */
            .stats-container {
                padding: 10px;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin-bottom: 15px;
            }
            
            .stat-item {
                padding: 10px;
                border-radius: 6px;
                border-left: 4px solid #6c757d;
            }
            
            .stat-label {
                display: block;
                font-weight: bold;
                margin-bottom: 5px;
            }
            
            .stat-numbers {
                display: flex;
                align-items: baseline;
            }
            
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                margin-right: 5px;
            }
            
            .stat-percentage {
                color: #6c757d;
            }
            
            /* Power score */
            .power-score-container {
                text-align: center;
                margin-top: 15px;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 8px;
            }
            
            .power-score-value {
                font-size: 48px;
                font-weight: bold;
                color: #2c3e50;
                margin: 0;
            }
            
            .power-score-label {
                font-size: 16px;
                color: #6c757d;
            }
            
            /* Countries list section */
            .countries-row {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.1);
                padding: 15px;
                margin-bottom: 20px;
            }
            
            .countries-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 15px;
            }
            
            .requirement-category {
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            }
            
            .category-header {
                display: flex;
                justify-content: space-between;
                padding: 10px 15px;
                color: white;
            }
            
            .category-label {
                font-weight: bold;
            }
            
            .category-count {
                background-color: rgba(255,255,255,0.3);
                border-radius: 20px;
                padding: 2px 8px;
                font-size: 14px;
            }
            
            .countries-list-container {
                max-height: 300px;
                overflow-y: auto;
                padding: 10px;
                background-color: #f8f9fa;
            }
            
            .countries-list {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 5px;
                list-style-type: none;
                padding: 0;
                margin: 0;
            }
            
            .country-item {
                padding: 5px;
                font-size: 14px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            
            /* Footer */
            .footer {
                text-align: center;
                padding: 20px 0;
                margin-top: 20px;
                border-top: 1px solid #dee2e6;
                color: #6c757d;
            }
            
            .footer a {
                color: #007bff;
                text-decoration: none;
            }
            
            .footer a:hover {
                text-decoration: underline;
            }
            
            /* Responsive adjustments */
            @media (max-width: 768px) {
                .stats-grid {
                    grid-template-columns: 1fr;
                }
                
                .data-row {
                    flex-direction: column;
                }
                
                .countries-list {
                    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Allow the server to be run if this file is executed
app_handle = app.server
if __name__ == '__main__':
    app.run_server(debug=True)
