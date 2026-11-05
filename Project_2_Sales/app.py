import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Analysis Dashboard", page_icon="📊", layout="wide")
st.title("📊 Sales Data Analysis Dashboard")
st.caption("Academic demonstration using simulated sales records.")

@st.cache_data
def load_data():
    df = pd.read_csv("sales_data.csv")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("sales_data.csv nahi mila. Is CSV ko app.py ke same folder mein rakhein.")
    st.stop()

st.sidebar.header("Dashboard Filters")
regions = st.sidebar.multiselect("Select regions", sorted(df["Region"].unique()),
                                 default=sorted(df["Region"].unique()))
segments = st.sidebar.multiselect("Select customer segments", sorted(df["Segment"].unique()),
                                  default=sorted(df["Segment"].unique()))
products = st.sidebar.multiselect("Select products", sorted(df["Product"].unique()),
                                  default=sorted(df["Product"].unique()))

filtered = df[
    df["Region"].isin(regions) &
    df["Segment"].isin(segments) &
    df["Product"].isin(products)
].copy()

if filtered.empty:
    st.warning("Selected filters ke liye records nahi mile.")
    st.stop()

total_sales = filtered["Sales"].sum()
total_profit = filtered["Profit"].sum()
total_orders = filtered["Order_ID"].nunique()
total_quantity = filtered["Quantity"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"₹{total_sales:,.0f}")
c2.metric("Total Profit", f"₹{total_profit:,.0f}")
c3.metric("Total Orders", f"{total_orders:,}")
c4.metric("Units Sold", f"{total_quantity:,}")

filtered["Month"] = filtered["Order_Date"].dt.to_period("M").astype(str)
monthly = filtered.groupby("Month", as_index=False)[["Sales", "Profit"]].sum()

st.subheader("Monthly Sales and Profit")
fig = px.line(monthly, x="Month", y=["Sales", "Profit"], markers=True,
              title="Monthly sales and profit trend")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Sales by Customer Segment")
    segment_data = filtered.groupby("Segment", as_index=False)["Sales"].sum()
    fig2 = px.pie(segment_data, names="Segment", values="Sales", hole=0.35)
    st.plotly_chart(fig2, use_container_width=True)
with right:
    st.subheader("Product-wise Sales")
    product_data = filtered.groupby("Product", as_index=False)["Sales"].sum().sort_values("Sales", ascending=False)
    fig3 = px.bar(product_data, x="Product", y="Sales", color="Product")
    st.plotly_chart(fig3, use_container_width=True)

st.subheader("Regional Performance")
region_data = filtered.groupby("Region", as_index=False)[["Sales", "Profit"]].sum()
fig4 = px.bar(region_data, x="Region", y=["Sales", "Profit"], barmode="group")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Customer Summary")
customer_data = filtered.groupby("Customer_ID", as_index=False).agg(
    Orders=("Order_ID", "nunique"), Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum")
).sort_values("Total_Sales", ascending=False)
st.dataframe(customer_data, use_container_width=True)

st.subheader("Filtered Sales Records")
st.dataframe(filtered.drop(columns=["Month"]), use_container_width=True)
st.download_button("Download filtered CSV",
                   data=filtered.drop(columns=["Month"]).to_csv(index=False).encode("utf-8"),
                   file_name="sales_filtered_data.csv", mime="text/csv")
