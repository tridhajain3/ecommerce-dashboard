import streamlit as st
import pandas as pd
from collections import defaultdict

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="E-Commerce Intelligence Platform",
    layout="wide"
)

# =====================================================
# GLASS UI CSS
# =====================================================
st.markdown("""
<style>

/* Background */
body {
    background: linear-gradient(135deg, #0b0f19, #111827);
    color: white;
}

/* Glass Card */
.glass-card {
    background: rgba(255, 255, 255, 0.06);
    border-radius: 18px;
    padding: 18px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.08);
    transition: 0.3s ease;
}

.glass-card:hover {
    transform: translateY(-5px);
    background: rgba(255, 255, 255, 0.1);
}

/* Titles */
.title {
    font-size: 28px;
    font-weight: 800;
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: rgba(17, 24, 39, 0.7);
    backdrop-filter: blur(10px);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD DATA (CACHED)
# =====================================================
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_online_retail.csv")
    df = df.dropna(subset=["Description", "CustomerID"])
    return df

df = load_data()

# =====================================================
# GLOBAL METRICS
# =====================================================
TOTAL_REVENUE = df["Quantity"].sum() * df["UnitPrice"].mean()
TOTAL_ORDERS = df["InvoiceNo"].nunique()
TOTAL_CUSTOMERS = df["CustomerID"].nunique()
TOTAL_PRODUCTS = df["Description"].nunique()

# =====================================================
# BUILD GRAPH (DSA)
# =====================================================
@st.cache_data
def build_graph(data):
    graph = defaultdict(set)

    for _, group in data.groupby("InvoiceNo"):
        products = group["Description"].unique()

        for i in range(len(products)):
            for j in range(i + 1, len(products)):
                graph[products[i]].add(products[j])
                graph[products[j]].add(products[i])

    return graph

product_graph = build_graph(df)

def recommend(product, top_n=6):
    if product not in product_graph:
        return []
    return list(product_graph[product])[:top_n]

# =====================================================
# SIDEBAR NAVIGATION (NETFLIX STYLE)
# =====================================================
st.sidebar.title("🎬 Navigation")

page = st.sidebar.radio(
    "",
    [
        "🏠 Home",
        "📊 Analytics",
        "📦 Products",
        "👤 Customers",
        "🧠 Insights",
        "🤖 AI Recommender"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("E-Commerce Intelligence System")

# =====================================================
# HOME PAGE
# =====================================================
if page == "🏠 Home":

    st.markdown('<div class="title">🛒 E-Commerce Dashboard</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"""
    <div class="glass-card">
        <h4>Revenue</h4>
        <h2>£{TOTAL_REVENUE:,.0f}</h2>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="glass-card">
        <h4>Orders</h4>
        <h2>{TOTAL_ORDERS}</h2>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="glass-card">
        <h4>Customers</h4>
        <h2>{TOTAL_CUSTOMERS}</h2>
    </div>
    """, unsafe_allow_html=True)

    col4.markdown(f"""
    <div class="glass-card">
        <h4>Products</h4>
        <h2>{TOTAL_PRODUCTS}</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("📈 Monthly Trend")
        st.line_chart(df.groupby("Month")["Quantity"].sum())

    with c2:
        st.subheader("⏰ Hourly Activity")
        st.bar_chart(df.groupby("Hour")["Quantity"].sum())

# =====================================================
# ANALYTICS
# =====================================================
elif page == "📊 Analytics":

    st.title("📊 Sales Analytics")

    st.bar_chart(
        df.groupby("Country")["Quantity"]
        .sum()
        .sort_values(ascending=True)
    )

    st.line_chart(df.groupby("Month")["Quantity"].sum())

# =====================================================
# PRODUCTS
# =====================================================
elif page == "📦 Products":

    st.title("📦 Product Analytics")

    st.bar_chart(
        df.groupby("Description")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

# =====================================================
# CUSTOMERS
# =====================================================
elif page == "👤 Customers":

    st.title("👤 Customer Analytics")

    st.bar_chart(
        df.groupby("CustomerID")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

# =====================================================
# INSIGHTS
# =====================================================
elif page == "🧠 Insights":

    st.title("🧠 Business Insights")

    top_product = df.groupby("Description")["Quantity"].sum().idxmax()
    top_country = df.groupby("Country")["Quantity"].sum().idxmax()

    col1, col2, col3 = st.columns(3)

    col1.metric("🏆 Top Product", top_product)
    col2.metric("🌍 Top Country", top_country)
    col3.metric("💰 Revenue", f"£{TOTAL_REVENUE:,.0f}")

    st.success("📌 UK dominates sales globally")
    st.info("📌 Peak activity: 10 AM – 2 PM")

# =====================================================
# AI RECOMMENDER
# =====================================================
elif page == "🤖 AI Recommender":

    st.markdown('<div class="title">🤖 Recommendation Engine</div>', unsafe_allow_html=True)

    product = st.selectbox(
        "Select Product",
        df["Description"].unique()
    )

    recs = recommend(product)

    st.markdown("### 🎯 Customers also bought:")

    if recs:
        cols = st.columns(3)

        for i, r in enumerate(recs):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="glass-card">
                    📦 {r}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("No recommendations found")