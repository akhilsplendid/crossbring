import os
import requests
import pandas as pd
import streamlit as st

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Crossbring Dashboard", layout="wide")
st.title("Crossbring — Swedish Job Market Dashboard")
st.caption("Data sourced via ETL into PostgreSQL; served by FastAPI")

@st.cache_data(ttl=60)
def fetch_jobs(limit: int = 200):
    r = requests.get(f"{API_URL}/jobs", params={"limit": limit}, timeout=15)
    r.raise_for_status()
    return r.json()


try:
    data = fetch_jobs(500)
    df = pd.DataFrame(data)
    if df.empty:
        st.info("No job data yet. Trigger the Airflow DAG `job_etl_pipeline`, then refresh.")
    else:
        st.subheader("Jobs Table")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Jobs by Location")
        if "location" in df.columns:
            loc_counts = df["location"].fillna("Unknown").value_counts().reset_index()
            loc_counts.columns = ["location", "count"]
            st.bar_chart(loc_counts.set_index("location"))

        st.subheader("Jobs by Company")
        if "company" in df.columns:
            comp_counts = df["company"].fillna("Unknown").value_counts().reset_index()
            comp_counts.columns = ["company", "count"]
            st.bar_chart(comp_counts.set_index("company"))
except Exception as e:
    st.error(f"Failed to load data from API at {API_URL}: {e}")

