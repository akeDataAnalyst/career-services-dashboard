import streamlit as st
import pandas as pd
import mysql.connector
import os
import plotly.express as px
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# --- Print for debugging to confirm .env file is loaded ---
print("Attempting to load database configuration...")
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_DATABASE")
}
print(f"Database Config: {db_config}")
print("-" * 20)

def get_data():
    """Connects to MySQL and fetches data from dbt models."""
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(**db_config)
        print("Successfully connected to MySQL database.")
        
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
        print(f"Error fetching data from MySQL: {e}")
        st.error(f"Error fetching data from MySQL: {e}. Please check your database connection.")
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

# Check if the DataFrame is empty and display a warning
if df.empty:
    st.warning("No data found. Please ensure your database is running and dbt models have been built. Check the terminal for error messages.")
else:
    # Convert 'registration_date_x' to datetime objects
    df['registration_date'] = pd.to_datetime(df['registration_date_x'])

    # Streamlit App Layout
    st.title('Career Services User Behavior Analytics')
    st.markdown("This dashboard provides a comprehensive overview of user behavior on the career services platform.")

    # --- DAU/MAU Graph ---
    st.header('Daily Active Users (DAU)')
    dau_df = df.groupby(df['registration_date'].dt.date)['user_id'].nunique().reset_index()
    dau_df.columns = ['Date', 'DAU']
    dau_fig = px.line(dau_df, x='Date', y='DAU', title='Daily Active Users Over Time')
    st.plotly_chart(dau_fig, use_container_width=True)

    # --- User Acquisition by Country Graph ---
    st.header('User Acquisition by Country')
    country_df = df.groupby('country')['user_id'].count().reset_index()
    country_df.columns = ['Country', 'User Count']
    country_fig = px.bar(country_df, x='Country', y='User Count', title='User Acquisition by Country')
    st.plotly_chart(country_fig, use_container_width=True)

    # --- Feature Adoption Graph ---
    st.header('Feature Adoption Rates')
    total_users = len(df['user_id'].unique())
    if total_users > 0:
        adoption_rates = {
            'Resumes Uploaded': (df['total_resumes_uploaded'] > 0).sum() / total_users,
            'Applications Submitted': (df['total_applications'] > 0).sum() / total_users,
            'Courses Enrolled': (df['total_courses_enrolled'] > 0).sum() / total_users,
            'Assessments Taken': (df['total_assessments_taken'] > 0).sum() / total_users,
        }
        adoption_df = pd.DataFrame(adoption_rates.items(), columns=['Feature', 'Adoption Rate'])
        adoption_fig = px.bar(adoption_df, x='Feature', y='Adoption Rate', title='Feature Adoption Rates')
        adoption_fig.update_layout(yaxis_tickformat='.0%')
        st.plotly_chart(adoption_fig, use_container_width=True)
    else:
        st.write("Not enough data to calculate feature adoption.")

    # --- Raw Data Display (Optional) ---
    st.header('Raw Data')
    st.write("A sample of the combined data from dbt models.")
    st.dataframe(df.head())
