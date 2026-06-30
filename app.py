
import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv(
        "cleaned_online_retail.csv",
        encoding="ISO-8859-1"
    )

    # convert date column
    if "InvoiceDate" in df.columns:
        df["InvoiceDate"] = pd.to_datetime(
            df["InvoiceDate"],
            errors="coerce"
        )

    # create revenue column if missing
    if "Revenue" not in df.columns:
        if "Quantity" in df.columns and "UnitPrice" in df.columns:
            df["Revenue"] = (
                df["Quantity"] *
                df["UnitPrice"]
            )

    return df


df = load_data()

# =========================================================
# TITLE
# =========================================================
st.title("📊 E-Commerce Analytics Dashboard")
st.markdown(
    "Interactive business intelligence dashboard with filters, KPIs, visualizations and detailed records."
)

# =========================================================
# FILTER SECTION
# =========================================================
st.markdown("## Filters")

col1, col2, col3 = st.columns(3)

with col1:
    start_date = st.date_input(
        "Filter From",
        df["InvoiceDate"].min()
    )

with col2:
    end_date = st.date_input(
        "Filter To",
        df["InvoiceDate"].max()
    )

with col3:
    if "Country" in df.columns:
        category = st.selectbox(
            "Filter by Category",
            ["All"] + sorted(df["Country"].dropna().unique().tolist())
        )
    else:
        category = "All"

# =========================================================
# APPLY FILTERS
# =========================================================
filtered_df = df[
    (df["InvoiceDate"] >= pd.to_datetime(start_date)) &
    (df["InvoiceDate"] <= pd.to_datetime(end_date))
]

if category != "All":
    filtered_df = filtered_df[
        filtered_df["Country"] == category
    ]

# =========================================================
# KPI SECTION
# =========================================================
st.markdown("## Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df["Revenue"].sum()
total_orders = filtered_df["InvoiceNo"].nunique()
avg_order = total_revenue / max(total_orders, 1)

if "Country" in filtered_df.columns:
    top_category = (
        filtered_df.groupby("Country")["Revenue"]
        .sum()
        .idxmax()
    )
else:
    top_category = "N/A"

with col1:
    st.metric(
        "Total Revenue",
        f"${total_revenue:,.0f}"
    )

with col2:
    st.metric(
        "Total Orders",
        f"{total_orders:,}"
    )

with col3:
    st.metric(
        "Average Order Value",
        f"${avg_order:,.0f}"
    )

with col4:
    st.metric(
        "Top Category",
        top_category
    )

# =========================================================
# VISUALIZATION SECTION
# =========================================================
st.markdown("## Visualizations")

chart_option = st.selectbox(
    "Select Visualization",
    [
        "Revenue Over Time",
        "Revenue by Country",
        "Top Products"
    ]
)

# Revenue Trend
if chart_option == "Revenue Over Time":

    chart = (
        filtered_df
        .groupby(
            filtered_df["InvoiceDate"].dt.to_period("M")
        )["Revenue"]
        .sum()
        .reset_index()
    )

    chart["InvoiceDate"] = chart[
        "InvoiceDate"
    ].astype(str)

    fig = px.line(
        chart,
        x="InvoiceDate",
        y="Revenue",
        title="Revenue Trend"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# Revenue by Country
elif chart_option == "Revenue by Country":

    chart = (
        filtered_df
        .groupby("Country")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        chart,
        x="Country",
        y="Revenue",
        title="Revenue by Country"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# Top Products
elif chart_option == "Top Products":

    chart = (
        filtered_df
        .groupby("Description")["Revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig = px.bar(
        chart,
        x="Description",
        y="Revenue",
        title="Top Products"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================================
# DOWNLOAD BUTTON
# =========================================================
st.download_button(
    "⬇ Download Filtered Report",
    filtered_df.to_csv(index=False),
    "filtered_report.csv",
    "text/csv"
)

# =========================================================
# RAW DATA
# =========================================================
st.markdown("## Raw Data Table")

st.dataframe(
    filtered_df,
    use_container_width=True
)