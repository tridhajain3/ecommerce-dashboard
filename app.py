
import streamlit as st
import pandas as pd

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="E-Commerce Dashboard",
    layout="wide"
)

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_online_retail.csv")
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    return df

df = load_data()

# =========================
# DASHBOARD TITLE
# =========================
st.title("📊 Dashboard Overview")
st.markdown("Clean analytical view of e-commerce sales performance")
st.markdown("---")

# =========================================================
# FILTERS SECTION (TOP ROW)
# =========================================================
st.subheader("🔎 Filters Section")

colf1, colf2, colf3 = st.columns(3)

with colf1:
    date_range = st.date_input(
        "Filter by Date",
        [df["InvoiceDate"].min(), df["InvoiceDate"].max()]
    )

with colf2:
    country_filter = st.multiselect(
        "Filter by Country",
        df["Country"].dropna().unique(),
        default=df["Country"].dropna().unique()
    )

with colf3:
    category_filter = st.multiselect(
        "Filter by Product Category",
        df["Description"].dropna().unique()
    )

# =========================
# APPLY FILTERS
# =========================
filtered_df = df[
    (df["InvoiceDate"].dt.date >= date_range[0]) &
    (df["InvoiceDate"].dt.date <= date_range[1]) &
    (df["Country"].isin(country_filter))
]

if category_filter:
    filtered_df = filtered_df[filtered_df["Description"].isin(category_filter)]

# =========================================================
# KPI SECTION
# =========================================================
st.markdown("---")
st.subheader("📌 Key Metrics")

total_revenue = filtered_df["Revenue"].sum()
total_orders = filtered_df["InvoiceNo"].nunique()
avg_order_value = total_revenue / total_orders if total_orders else 0
top_category = (
    filtered_df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .index[0]
    if len(filtered_df) > 0 else "N/A"
)

k1, k2, k3, k4 = st.columns(4)

k1.metric("💰 Total Revenue", f"£{total_revenue:,.0f}")
k2.metric("🧾 Total Orders", total_orders)
k3.metric("📊 Avg Order Value", f"£{avg_order_value:,.2f}")
k4.metric("🏆 Top Product", top_category)

# =========================================================
# VISUALIZATION SECTION
# =========================================================
st.markdown("---")
st.subheader("📈 Visualizations")

chart_option = st.selectbox(
    "Select View",
    ["Revenue Over Time", "Revenue by Country", "Top Products"]
)

# -------------------------
# 1. Revenue Over Time
# -------------------------
if chart_option == "Revenue Over Time":

    revenue_time = filtered_df.groupby(
        filtered_df["InvoiceDate"].dt.to_period("M")
    )["Revenue"].sum()

    revenue_time.index = revenue_time.index.astype(str)

    st.line_chart(revenue_time)

# -------------------------
# 2. Revenue by Country
# -------------------------
elif chart_option == "Revenue by Country":

    country_rev = filtered_df.groupby("Country")["Revenue"].sum().sort_values(ascending=False)

    st.bar_chart(country_rev)

# -------------------------
# 3. Top Products
# -------------------------
elif chart_option == "Top Products":

    product_rev = filtered_df.groupby("Description")["Revenue"].sum().sort_values(ascending=False).head(10)

    st.bar_chart(product_rev)

# =========================================================
# RAW DATA SECTION
# =========================================================
st.markdown("---")
st.subheader("📄 Raw Data Table")

st.dataframe(filtered_df, use_container_width=True)