import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

DB_NAME = "mlb_almanac.db"

@st.cache_data
def get_years():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    years = [int(name.replace("mlb_almanac_", "")) for name in tables if name.startswith("mlb_almanac_")]
    conn.close()
    return sorted(years)

@st.cache_data
def load_data(year_range):
    conn = sqlite3.connect(DB_NAME)
    dfs = []
    for year in year_range:
        table_name = f"mlb_almanac_{year}"
        try:
            df = pd.read_sql_query(f"SELECT * FROM '{table_name}'", conn)
            dfs.append(df)
        except:
            continue
    conn.close()
    return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()

st.set_page_config(page_title="MLB Almanac Dashboard", layout="wide")
st.title("⚾ MLB Almanac Dashboard")

years = get_years()
year_range = st.slider("Select Year Range", min_value=years[0], max_value=years[-1], value=(years[-11], years[-1]))

df = load_data(range(year_range[0], year_range[1]+1))

if df.empty:
    st.warning("No data available for selected years.")
    st.stop()

all_stats = sorted(df["statistic"].dropna().unique())
selected_stat = st.selectbox("Select Statistic", all_stats)

top_n = st.slider("Top N Players", 1, 25, 10)

filtered = df[df["statistic"] == selected_stat].copy()
filtered["value"] = pd.to_numeric(filtered["value"], errors="coerce")
filtered = filtered.dropna(subset=["value"])
filtered = filtered.sort_values(by="value", ascending=False).head(top_n)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏅 Top Players")
    fig1 = px.bar(filtered, x="name", y="value", color="team",
                title=f"Top {top_n} - {selected_stat} ({year_range[0]}–{year_range[1]})")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("📊 Team Distribution")
    fig2 = px.pie(filtered, names="team", title="Team Representation Among Top Players")
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("📈 Trend Over Time")

@st.cache_data
def get_stat_trend(stat, year_range):
    conn = sqlite3.connect(DB_NAME)
    trend_data = []
    for year in range(year_range[0], year_range[1] + 1):
        try:
            df_year = pd.read_sql_query(f"SELECT * FROM mlb_almanac_{year}", conn)
            df_year = df_year[df_year["statistic"] == stat]
            df_year["value"] = pd.to_numeric(df_year["value"], errors="coerce")
            avg_val = df_year["value"].dropna().mean()
            trend_data.append((year, avg_val))
        except:
            continue
    conn.close()
    return pd.DataFrame(trend_data, columns=["year", "avg_value"])

trend_df = get_stat_trend(selected_stat, year_range)
fig3 = px.line(trend_df, x="year", y="avg_value", markers=True,
            title=f"Average {selected_stat} ({year_range[0]}–{year_range[1]})")
st.plotly_chart(fig3, use_container_width=True)
