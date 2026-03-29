import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page Config
st.set_page_config(page_title="Nigeria Security Analysis", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    df = pd.read_csv('Incident_Data_Perfectly_Cleaned.csv')
    df['Start date'] = pd.to_datetime(df['Start date'])
    df['Year'] = df['Start date'].dt.year
    df['Month'] = df['Start date'].dt.month_name()
    df['Day_of_Week'] = df['Start date'].dt.day_name()
    return df

df = load_data()

# Header
st.title("🇳🇬 Nigeria Security Incident Intelligence Dashboard")
st.markdown("---")

# Sidebar Filters
st.sidebar.header("Data Filters")
years = st.sidebar.multiselect("Select Year(s)", options=sorted(df['Year'].unique()), default=df['Year'].unique())
states = st.sidebar.multiselect("Select State(s)", options=sorted(df['State'].unique()), default=df['State'].unique())

# Filtering logic
filtered_df = df[(df['Year'].isin(years)) & (df['State'].isin(states))]

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Incidents", len(filtered_df))
col2.metric("Total Fatalities", int(filtered_df['Number of deaths'].sum()))
col3.metric("Avg Deaths/Incident", round(filtered_df['Number of deaths'].mean(), 2))
col4.metric("Top Hotspot", filtered_df['State'].value_counts().idxmax())

st.markdown("---")

# Tabs for the 10 Questions
tab_vol, tab_geo, tab_time, tab_patterns = st.tabs(["Volume & Severity", "Geography", "Time Trends", "Deep Insights"])

with tab_vol:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Q1: Incident Frequency")
        counts = filtered_df['Incident_Type'].value_counts().head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=counts.values, y=counts.index, hue=counts.index, palette='viridis', legend=False)
        st.pyplot(fig)
    
    with c2:
        st.subheader("Q5: Severity (Total Deaths)")
        severity = filtered_df.groupby('Incident_Type')['Number of deaths'].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots()
        sns.barplot(x=severity.values, y=severity.index, hue=severity.index, palette='Reds_r', legend=False)
        st.pyplot(fig)

with tab_geo:
    st.subheader("Q2 & Q6: Regional Analysis")
    c1, c2 = st.columns([1, 2])
    with c1:
        state_counts = filtered_df['State'].value_counts().head(10)
        st.dataframe(state_counts)
    with c2:
        st.write("Correlation: State vs Incident Type")
        top_states = filtered_df['State'].value_counts().nlargest(5).index
        top_types = filtered_df['Incident_Type'].value_counts().nlargest(5).index
        ct = pd.crosstab(filtered_df[filtered_df['State'].isin(top_states)]['State'], 
                         filtered_df[filtered_df['Incident_Type'].isin(top_types)]['Incident_Type'])
        fig, ax = plt.subplots()
        sns.heatmap(ct, annot=True, cmap="YlGnBu", fmt='d')
        st.pyplot(fig)

with tab_time:
    st.subheader("Q4, Q7 & Q9: Temporal Patterns")
    time_choice = st.selectbox("View by:", ["Yearly", "Day of Week", "Daily Trend"])
    
    if time_choice == "Yearly":
        st.bar_chart(filtered_df['Year'].value_counts().sort_index())
    elif time_choice == "Day of Week":
        order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_counts = filtered_df['Day_of_Week'].value_counts().reindex(order)
        st.bar_chart(day_counts)
    else:
        daily = filtered_df.groupby('Start date').size()
        st.line_chart(daily)

with tab_patterns:
    st.subheader("Q8 & Q10: Strategic Insights")
    st.write("Lethality Pattern: Average Deaths per Incident Type")
    lethality = filtered_df.groupby('Incident_Type')['Number of deaths'].mean().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots()
    sns.barplot(x=lethality.values, y=lethality.index, hue=lethality.index, palette='flare', legend=False)
    st.pyplot(fig)
    
    st.info("**Data-Driven Insight:** Focus intervention on the top-ranked lethal categories above to reduce the overall fatality rate effectively.")