import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Page Configuration
st.set_page_config(page_title="Nigeria Security Intelligence", layout="wide")

# 2. Advanced Data Loading & Auto-Cleaning Function
@st.cache_data
def load_data():
    # Load the cleaned CSV
    df = pd.read_csv('Incident_Data_Perfectly_Cleaned.csv')
    
    # --- INTERNAL AUTO-CLEANING (Safety Net) ---
    # 1. Standardize States to Title Case & Strip Spaces
    df['State'] = df['State'].astype(str).str.strip().str.title()
    
    # 2. Merge all Abuja/FCT variants into one
    fct_map = {
        'Abuja (Fct)': 'FCT Abuja', 'Fct ( Abuja)': 'FCT Abuja', 
        'Fct (Abuja)': 'FCT Abuja', 'Fct(Abuja)': 'FCT Abuja', 
        'Fct, ( Abuja)': 'FCT Abuja', 'Fct, (Abuja)': 'FCT Abuja', 
        'Fct, Abuja': 'FCT Abuja', 'Fct': 'FCT Abuja', 'Abuja': 'FCT Abuja'
    }
    df['State'] = df['State'].replace(fct_map)
    
    # 3. Fix common typos found in the 94-state list
    typo_map = {
        'Anmabra': 'Anambra', 'Bornon': 'Borno', 'Cross Rivers': 'Cross River',
        'Jiagawa': 'Jigawa', 'Jigaawa': 'Jigawa', 'Kadauna': 'Kaduna',
        'Katisna': 'Katsina', 'Nasaraawa': 'Nasarawa', 'Zamafara': 'Zamfara'
    }
    df['State'] = df['State'].replace(typo_map)
    
    # 4. Remove 'State' from names (e.g., "Kano State" -> "Kano")
    df['State'] = df['State'].str.replace(' State', '', case=False)
    
    # 5. Drop "Noise" rows like 'Unknown' or person names
    noise = ['Unknown', 'Hamza Musa', 'Nan', 'None', '']
    df = df[~df['State'].isin(noise)]
    
    # 6. Standardize Incident Types
    df['Incident_Type'] = df['Incident_Type'].astype(str).str.strip().str.title()
    
    # 7. Date & Time processing
    df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')
    df['Year'] = df['Start date'].dt.year.fillna(0).astype(int)
    df['Day_of_Week'] = df['Start date'].dt.day_name()
    df['Number of deaths'] = pd.to_numeric(df['Number of deaths'], errors='coerce').fillna(0)
    
    return df

# Initialize Data
df = load_data()

# 3. Header & Dynamic Counter
st.title("🇳🇬 Nigeria Security Incident Intelligence Dashboard")
st.subheader(f"📍 Analyzing Data across {df['State'].nunique()} Standardized Regions")
st.markdown("---")

# 4. Sidebar Filters
st.sidebar.header("Filter Analytics")

# Year Filter (Removing 0s from the selector)
years = sorted([y for y in df['Year'].unique() if y > 1900])
selected_years = st.sidebar.multiselect("Select Year(s)", options=years, default=years)

# State Filter
states = sorted(df['State'].unique())
selected_states = st.sidebar.multiselect("Select State(s)", options=states, default=states)

# Apply Filter Logic
mask = (df['Year'].isin(selected_years)) & (df['State'].isin(selected_states))
filtered_df = df[mask]

# 5. Top Level Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Total Incidents", f"{len(filtered_df):,}")
m2.metric("Total Fatalities", f"{int(filtered_df['Number of deaths'].sum()):,}")
m3.metric("Avg Deaths per Incident", f"{filtered_df['Number of deaths'].mean():.2f}")

st.markdown("---")

# 6. Visualization Tabs
tab1, tab2, tab3 = st.tabs(["📊 Frequency & Severity", "🕒 Time Patterns", "📋 Data View"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Top 10 Incident Types")
        counts = filtered_df['Incident_Type'].value_counts().head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=counts.values, y=counts.index, hue=counts.index, palette='viridis', legend=False)
        st.pyplot(fig)
        
    with col2:
        st.write("### Deadliest Regions (Top 10)")
        deaths = filtered_df.groupby('State')['Number of deaths'].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=deaths.values, y=deaths.index, hue=deaths.index, palette='Reds_r', legend=False)
        st.pyplot(fig)

with tab2:
    st.write("### Incident Volume by Day of the Week")
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_stats = filtered_df['Day_of_Week'].value
