import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard: Site Revenue", layout="wide")
st.title("📊 Site Revenue Overview — Daily Breakdown")

# --------------------------
# File upload + session state
# --------------------------

uploaded_file = st.file_uploader("📁 Upload your CSV file", type=["csv"])

# Initial read if file just uploaded
if uploaded_file is not None and "df" not in st.session_state:
    df = pd.read_csv(uploaded_file)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
    df = df.dropna(subset=['date', 'revenue'])
    st.session_state['df'] = df
    st.success("✅ File successfully loaded.")
    st.dataframe(df.head(), use_container_width=True)

# File already in session
elif "df" in st.session_state:
    df = st.session_state['df']
    st.info("ℹ️ Using previously uploaded file.")

# Fallback to default
else:
    @st.cache_data
    def load_default_data():
        df = pd.read_csv("data.csv")
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')
        return df.dropna(subset=['date', 'revenue'])
    
    df = load_default_data()
    st.info("ℹ️ Using default data.csv from repository")

# Optional reset button
if st.button("🔄 Reset uploaded file"):
    st.session_state.pop("df", None)
    st.rerun()

# --------------------------
# Grouping and Visualization
# --------------------------

grouped = df.groupby(['site', 'date'])['revenue'].sum().reset_index()
site_max = grouped.groupby('site')['revenue'].max().reset_index()
site_max['group'] = pd.qcut(site_max['revenue'], q=3, labels=['low', 'medium', 'high'])
grouped = grouped.merge(site_max[['site', 'group']], on='site', how='left')

# UI filters
available_groups = grouped['group'].dropna().unique().tolist()
group_choice = st.selectbox("Select a Site Revenue Group", available_groups)
show_markers = st.checkbox("Show markers on lines", value=True)

df_group = grouped[grouped['group'] == group_choice]

# Plot
if df_group.empty:
    st.warning("No data available for the selected group.")
else:
    fig = px.line(
        df_group, x='date', y='revenue', color='site',
        title=f"Sites with {group_choice} Revenue",
        markers=show_markers
    )
    fig.update_layout(hovermode='x unified', height=500)
    st.plotly_chart(fig, use_container_width=True)