
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="E-Commerce Intelligence Dashboard",
    layout="wide"
)

# =====================================================
# SAMPLE DATA LOAD (replace with your CSV if needed)
# df = pd.read_csv("data.csv")
# =====================================================

@st.cache_data
def load_data():
    df = pd.read_csv("data.csv", encoding="ISO-8859-1")

    # basic cleaning
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

    return df

df = load_data()

# =====================================================
# SIDEBAR NAVIGATION (FIXED LABEL ISSUE)
# =====================================================
with st.sidebar:
    st.markdown("## 🧭 Navigation")

    page = st.radio(
        "",
        ["🏠 Overview", "📊 Dashboard", "📥 Reports"],
        label_visibility="collapsed"
    )

# =====================================================
# FILTER SECTION (GLOBAL)
# =====================================================
st.title("📦 E-Commerce Analytics Dashboard")

st.markdown("## 🔎 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    start_date = st.date_input("Start Date", df["InvoiceDate"].min())

with col2:
    end_date = st.date_input("End Date", df["InvoiceDate"].max())

with col3:
    country = st.selectbox("Country", ["All"] + list(df["Country"].unique()))

# Apply filters
filtered_df = df[
    (df["InvoiceDate"].dt.date >= start_date) &
    (df["InvoiceDate"].dt.date <= end_date)
]

if country != "All":
    filtered_df = filtered_df[filtered_df["Country"] == country]

# =====================================================
# KPI SECTION
# =====================================================
total_revenue = filtered_df["Revenue"].sum()
total_orders = filtered_df["InvoiceNo"].nunique()
avg_order_value = total_revenue / total_orders if total_orders else 0
top_category = filtered_df.groupby("Description")["Revenue"].sum().idxmax()

st.markdown("## 📊 Key Metrics")

k1, k2, k3, k4 = st.columns(4)

k1.metric("Total Revenue", f"₹ {total_revenue:,.2f}")
k2.metric("Total Orders", total_orders)
k3.metric("Avg Order Value", f"₹ {avg_order_value:,.2f}")
k4.metric("Top Product", top_category)

# =====================================================
# VISUALIZATION SECTION
# =====================================================
st.markdown("## 📈 Visual Insights")

chart_option = st.selectbox(
    "Choose Chart View",
    ["Revenue Over Time", "Revenue by Country", "Top Products"]
)

if chart_option == "Revenue Over Time":

    revenue_time = filtered_df.groupby(
        filtered_df["InvoiceDate"].dt.to_period("M")
    )["Revenue"].sum().reset_index()

    revenue_time["InvoiceDate"] = revenue_time["InvoiceDate"].astype(str)

    fig = px.line(
        revenue_time,
        x="InvoiceDate",
        y="Revenue",
        title="Revenue Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Revenue by Country":

    country_rev = filtered_df.groupby("Country")["Revenue"].sum().reset_index()

    fig = px.bar(
        country_rev,
        x="Country",
        y="Revenue",
        title="Revenue by Country"
    )
    st.plotly_chart(fig, use_container_width=True)

elif chart_option == "Top Products":

    product_rev = filtered_df.groupby("Description")["Revenue"].sum().reset_index()
    product_rev = product_rev.sort_values("Revenue", ascending=False).head(10)

    fig = px.bar(
        product_rev,
        x="Description",
        y="Revenue",
        title="Top 10 Products"
    )
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# DOWNLOAD REPORT SECTION
# =====================================================
st.markdown("## 📥 Download Report")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇ Download Filtered Data (CSV)",
    data=csv,
    file_name="ecommerce_report.csv",
    mime="text/csv"
)

# =====================================================
# RAW DATA
# =====================================================
st.markdown("## 📄 Raw Data")
st.dataframe(filtered_df, use_container_width=True)