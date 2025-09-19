import os
from dotenv import load_dotenv
import pandas as pd
import mysql.connector
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load environment variables from the .env file
load_dotenv()

# Database connection details, now securely read from environment variables
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE")
}

def get_data():
    """Connects to MySQL and fetches data from dbt models."""
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        
        # Use a cursor with dictionary=True to ensure column names are returned as keys
        cursor = conn.cursor(dictionary=True)
        
        # Fetch data from the fact table
        query_fact = "SELECT * FROM fact_user_activity"
        cursor.execute(query_fact)
        fact_df = pd.DataFrame(cursor.fetchall())
        
        # Fetch data from the dimension table
        query_dim = "SELECT * FROM dim_users"
        cursor.execute(query_dim)
        dim_df = pd.DataFrame(cursor.fetchall())
        
        return fact_df, dim_df
        
    except mysql.connector.Error as e:
        print(f"Error fetching data: {e}")
        # Return empty DataFrames on error to prevent the app from crashing
        return pd.DataFrame(), pd.DataFrame()
    finally:
        # Ensure the connection is closed
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# Fetch and merge the dataframes when the script starts
fact_df, dim_df = get_data()
df = pd.merge(fact_df, dim_df, on='user_id', how='left')

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div(children=[
    html.H1(children='Career Services User Behavior Analytics', style={'textAlign': 'center'}),
    
    html.Div(className='container', children=[
        html.Div(className='graph-card', children=[
            dcc.Graph(id='dau-mau-graph'),
        ]),
        html.Div(className='graph-card', children=[
            dcc.Graph(id='country-graph'),
        ]),
        html.Div(className='graph-card', children=[
            dcc.Graph(id='feature-adoption-graph'),
        ])
    ])
])

# Create a callback to generate the DAU/MAU graph
@app.callback(
    Output('dau-mau-graph', 'figure'),
    [Input('dau-mau-graph', 'id')] # A dummy input to trigger the graph
)
def update_dau_mau_graph(input_value):
    if df.empty:
        return {}
    
    # Calculate DAU
    dau_df = df.groupby(pd.to_datetime(df['registration_date_x']).dt.date)['user_id'].nunique().reset_index()
    dau_df.columns = ['Date', 'DAU']
    
    # Create the graph figure
    fig = px.line(dau_df, x='Date', y='DAU', title='Daily Active Users')
    return fig

# Create a callback to generate the Country Distribution graph
@app.callback(
    Output('country-graph', 'figure'),
    [Input('country-graph', 'id')]
)
def update_country_graph(input_value):
    if df.empty:
        return {}

    country_counts = df['country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'User_Count']
    fig = px.bar(country_counts, x='Country', y='User_Count', title='Users by Country')
    return fig

# Create a callback to generate the Feature Adoption graph
@app.callback(
    Output('feature-adoption-graph', 'figure'),
    [Input('feature-adoption-graph', 'id')] # A dummy input
)
def update_feature_adoption_graph(input_value):
    if df.empty:
        return {}
        
    # Calculate feature adoption rates
    total_users = len(df['user_id'].unique())
    if total_users == 0:
        return {}

    adoption_rates = {
        'Resumes Uploaded': (df['total_resumes_uploaded'] > 0).sum() / total_users,
        'Applications Submitted': (df['total_applications'] > 0).sum() / total_users,
        'Courses Enrolled': (df['total_courses_enrolled'] > 0).sum() / total_users,
        'Assessments Taken': (df['total_assessments_taken'] > 0).sum() / total_users,
    }
    
    adoption_df = pd.DataFrame(adoption_rates.items(), columns=['Feature', 'Adoption Rate'])
    
    fig = px.bar(adoption_df, x='Feature', y='Adoption Rate', title='Feature Adoption Rates')
    fig.update_layout(yaxis_tickformat='.0%')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
