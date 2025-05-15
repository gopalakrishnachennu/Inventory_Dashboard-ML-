import streamlit as st
from inventory_manager import main  # Make sure this function returns the processed DataFrame

# Configure the page
st.set_page_config(page_title="Inventory Management", layout="wide")
st.title("📦 Inventory Management Dashboard")

# Load data
df = main()

# If data is successfully loaded
if not df.empty:
    # Sidebar Filters
    st.sidebar.header("🔍 Filter Options")

    # First Layer: Stocked vs Unstocked
    stock_filter = st.sidebar.radio(
        "Inventory Type:",
        options=["Stocked", "Unstocked"],
        index=0
    )
    if stock_filter == "Unstocked":
        df = df[df["UNSTOCK_ITEMS"] == 1]
    else:
        df = df[df["UNSTOCK_ITEMS"] == 0]

    # Second Layer: Brand Dropdown
    if "BRAND" in df.columns:
        brand_options = sorted(df["BRAND"].dropna().unique())
        selected_brand = st.sidebar.selectbox(
            "Select Brand:",
            options=["All"] + brand_options,
            index=0,
            key="brand_filter"
        )
        if selected_brand != "All":
            df = df[df["BRAND"] == selected_brand]

    # Third Layer: Type Dropdown
    if "TYPE" in df.columns:
        type_options = sorted(df["TYPE"].dropna().unique())
        selected_type = st.sidebar.selectbox(
            "Select Type:",
            options=["All"] + type_options,
            index=0,
            key="type_filter"
        )
        if selected_type != "All":
            df = df[df["TYPE"] == selected_type]

    # Summary Metrics
    total_items = len(df)
    slow_items = int(df["SLOW_ITEMS"].sum())
    reorder_items = int(df["NXT_ORDER"].sum())

    col1, col2, col3 = st.columns(3)
    col1.metric("🕗 Slow Items", slow_items)
    col2.metric("📦 Items Needing Reorder", reorder_items)
    col3.metric("🧺 Total Items", total_items)

    # Tabbed View
    tab1, tab2, tab3 = st.tabs(["📋 All Items", "🕗 Slow Items", "📦 Reorder Items"])

    with tab1:
        st.dataframe(df, use_container_width=True)

    with tab2:
        st.dataframe(df[df["SLOW_ITEMS"] == 1], use_container_width=True)

    with tab3:
        st.dataframe(df[df["NXT_ORDER"] == 1], use_container_width=True)

else:
    st.error("❌ Failed to load the inventory file.")
