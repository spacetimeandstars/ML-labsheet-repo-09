import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="COVID-19 Analysis Dashboard", page_icon="🦠", layout="wide")
st.title("🦠 COVID-19 Data Analysis Dashboard")
st.caption("Academic demonstration using simulated data — not official public-health statistics.")

@st.cache_data
def load_data():
    df = pd.read_csv("covid_data.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("covid_data.csv nahi mila. Is CSV ko app.py ke same folder mein rakhein.")
    st.stop()

st.sidebar.header("Dashboard Filters")
countries = st.sidebar.multiselect("Select countries", sorted(df["Country"].unique()),
                                   default=sorted(df["Country"].unique()))
min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Select date range", value=(min_date, max_date),
                                   min_value=min_date, max_value=max_date)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = df[
    df["Country"].isin(countries) &
    df["Date"].between(pd.Timestamp(start_date), pd.Timestamp(end_date))
].copy()

if filtered.empty:
    st.warning("Selected filters ke liye data available nahi hai.")
    st.stop()

latest = filtered.sort_values("Date").groupby("Country").tail(1)
total_cases = int(latest["Confirmed_Cases"].sum())
total_recovered = int(latest["Recovered"].sum())
total_deaths = int(latest["Deaths"].sum())
total_active = int(latest["Active_Cases"].sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Confirmed Cases", f"{total_cases:,}")
c2.metric("Recovered", f"{total_recovered:,}")
c3.metric("Deaths", f"{total_deaths:,}")
c4.metric("Active Cases", f"{total_active:,}")

st.subheader("Daily Confirmed Cases")
daily = filtered.groupby(["Date", "Country"], as_index=False)["Daily_Cases"].sum()
fig = px.line(daily, x="Date", y="Daily_Cases", color="Country",
              title="Daily COVID-style cases by country", markers=False)
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Country-wise Confirmed Cases")
    country_totals = latest.groupby("Country", as_index=False)["Confirmed_Cases"].sum()
    fig2 = px.bar(country_totals, x="Country", y="Confirmed_Cases", color="Country")
    st.plotly_chart(fig2, use_container_width=True)
with right:
    st.subheader("Recovery and Death Comparison")
    outcome = latest.melt(id_vars="Country", value_vars=["Recovered", "Deaths"],
                          var_name="Outcome", value_name="People")
    fig3 = px.bar(outcome, x="Country", y="People", color="Outcome", barmode="group")
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Vaccination Trend")
vax = filtered.groupby(["Date", "Country"], as_index=False)["Daily_Vaccinated"].sum()
fig4 = px.area(vax, x="Date", y="Daily_Vaccinated", color="Country",
               title="Daily vaccinations (simulated)")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Filtered Dataset")
st.dataframe(filtered, use_container_width=True)
st.download_button("Download filtered CSV",
                   data=filtered.to_csv(index=False).encode("utf-8"),
                   file_name="covid_filtered_data.csv", mime="text/csv")
