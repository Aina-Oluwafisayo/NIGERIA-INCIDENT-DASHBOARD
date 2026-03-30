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
    
    # Ensure columns are strings before manipulation to avoid AttributeErrors
    df['State'] = df['State'].fillna('Unknown').astype(str).str.strip().str.title()
    df['Incident_Type'] = df['Incident_Type'].fillna('Unknown').astype(str).str.strip().str.title()

    # Merge Abuja/FCT variants
    fct_map = {
        'Abuja (Fct)': 'FCT Abuja', 'Fct ( Abuja)': 'FCT Abuja', 
        'Fct (Abuja)': 'FCT Abuja', 'Fct(Abuja)': 'FCT Abuja', 
        'Fct, ( Abuja)': 'FCT Abuja', 'Fct, (Abuja)': 'FCT Abuja', 
        'Fct, Abuja': 'FCT Abuja', 'Fct': 'FCT Abuja', 'Abuja': 'FCT Abuja'
    }
    df['State'] = df['State'].replace(fct_map)
    
    # Fix common typos
    typo_map = {
        'Anmabra': 'Anambra', 'Bornon': 'Borno', 'Cross Rivers': 'Cross River',
        'Jiagawa': 'Jigawa', 'Jigaawa': 'Jigawa', 'Kadauna': 'Kaduna',
        'Katisna': 'Katsina', 'Nasaraawa': 'Nasarawa', 'Zamafara': 'Zamfara'
    }
    df['State'] = df['State'].replace(typo_map)
    
    # Remove 'State' from names
    df['State'] = df['State'].str.replace(' State', '', case=False)
    
    # Drop "Noise" rows
    noise = ['Unknown', 'Hamza Musa', 'Nan', 'None', '0', '']
    df = df[~df['State'].isin(noise)]
    
    # --- DATE PROCESSING (The part that caused the crash) ---
    # Force conversion - invalid dates become NaT (Not a Time)
    df['Start date'] = pd.to_datetime(df['Start date'], errors='coerce')
    
    # Drop rows where date is completely missing so .dt calls don't fail
    df = df.dropna(subset=['Start date'])
    
    # Now we can safely extract time features
    df['Year'] = df['Start date'].dt.year.astype(int)
    df['Day_of_Week'] = df['Start date'].dt.day_name()
    
    # Ensure deaths are numbers
    df['Number of deaths'] = pd.to_numeric(df['Number of deaths'], errors='coerce').fillna(0)
    
    return df

# Initialize Data
df = load_data()

# 3. Header & Dynamic Counter
st.title("🇳🇬 Nigeria Security Incident Intelligence Dashboard")
# Filter out the "0" year and old dates for the count
valid_df = df[df['Year'] > 2000]
st.subheader(f"📍 Analyzing Data across {valid_df['State'].nunique()} Standardized Regions")
st.markdown("---")

# 4. Sidebar Filters
st.sidebar.header("Filter Analytics")

# Year Filter (Only show real years)
years_options = sorted([int(y) for y in valid_df['Year'].unique()])
selected_years = st.sidebar.multiselect("Select Year(s)", options=years_options, default=years_options)

# State Filter (Sorted alphabetically)
state_options = sorted([str(s) for s in valid_df['State'].unique()])
selected_states = st.sidebar.multiselect("Select State(s)", options=state_options, default=state_options)

# Apply Filter Logic
mask = (df['Year'].isin(selected_years)) & (df['State'].isin(selected_states))
filtered_df = df[mask]

# 5. Top Level Metrics
if not filtered_df.empty:
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Incidents", f"{len(filtered_df):,}")
    m2.metric("Total Fatalities", f"{int(filtered_df['Number of deaths'].sum()):,}")
    m3.metric("Avg Deaths per Incident", f"{filtered_df['Number of deaths'].mean():.2f}")
else:
    st.warning("No data found for the selected filters.")

st.markdown("---")

# 6. Visualization Tabs
tab1, tab2, tab3 = st.tabs(["📊 Frequency & Severity", "🕒 Time Patterns", "📋 Data View"])

with tab1:
    col1, col2 = st.columns(2)
    if not filtered_df.empty:
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
    if not filtered_df.empty:
        st.write("### Incident Volume by Day of the Week")
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        # Reindexing ensures the days appear in order even if one day has 0 incidents
        day_stats = filtered_df['Day_of_Week'].value_counts().reindex(days_order).fillna(0)
        st.bar_chart(day_stats)
        
        st.write("### Yearly Trend")
        yearly_trend = filtered_df.groupby('Year').size()
        st.line_chart(yearly_trend)

with tab3:
    st.write("### Filtered Data Preview")
    st.dataframe(filtered_df)
