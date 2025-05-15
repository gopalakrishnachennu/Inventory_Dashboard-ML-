import streamlit as st
import pandas as pd
import plotly.express as px
from inventory_manager import main  # Load processed inventory data

st.set_page_config(page_title="📦 Inventory Management", layout="wide")
st.title("📦 Inventory Management Dashboard")

df = main()

if not df.empty:
    tab1, tab2 = st.tabs(["📊 Data Analytics", "📈 Visual Analytics"])

    with tab1:
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

        # Tabbed View for Table
        table1, table2, table3 = st.tabs(["📋 All Items", "🕗 Slow Items", "📦 Reorder Items"])

        with table1:
            st.dataframe(df, use_container_width=True)

        with table2:
            st.dataframe(df[df["SLOW_ITEMS"] == 1], use_container_width=True)

        with table3:
            st.dataframe(df[df["NXT_ORDER"] == 1], use_container_width=True)

    with tab2:
        st.sidebar.header("🔍 Filter Options")

        selected_brand = st.sidebar.selectbox("Select Brand:", ["All"] + sorted(df["BRAND"].dropna().unique().tolist()), key="viz_brand")
        if selected_brand != "All":
            df = df[df["BRAND"] == selected_brand]

        selected_type = st.sidebar.selectbox("Select Type:", ["All"] + sorted(df["TYPE"].dropna().unique().tolist()), key="viz_type")
        if selected_type != "All":
            df = df[df["TYPE"] == selected_type]

        st.subheader("📈 Weekly Sales Trend (Bar + Line)")
        df_melted = df.melt(
            id_vars=["BRAND", "TYPE"],
            value_vars=["FIRST", "SECON", "THIRD", "FOURT", "FIFTH", "SIXTH", "SEVEN", "EIGHT", "NINTH", "TENTH", "ELEVE", "TWELV"],
            var_name="Week",
            value_name="Sales"
        )
        sales_fig = px.line(df_melted, x="Week", y="Sales", color="BRAND", title="Weekly Sales by Brand")
        st.plotly_chart(sales_fig, use_container_width=True)

        st.subheader("🥧 Inventory Distribution by Brand")
        pie_fig = px.pie(df, names="BRAND", values="QTY_ON_HND", title="Stock Distribution by Brand")
        st.plotly_chart(pie_fig, use_container_width=True)

        st.subheader("📊 Inventory Distribution by Type")
        donut_fig = px.pie(df, names="TYPE", values="QTY_ON_HND", hole=0.4, title="Stock Distribution by Type")
        st.plotly_chart(donut_fig, use_container_width=True)

        st.subheader("🌡️ Price vs Sales Heatmap")
        heatmap_data = df.groupby(["PRICE", "AVG_WEEK"], as_index=False)["SALES"].sum()
        heatmap = px.density_heatmap(heatmap_data, x="PRICE", y="AVG_WEEK", z="SALES", color_continuous_scale="Viridis")
        st.plotly_chart(heatmap, use_container_width=True)

        st.subheader("📈 Forecast: Projected Stock Needs")
        df_forecast = df[["BRAND", "AVG_WEEK", "QTY_ON_HND"]].copy()
        df_forecast["Projected_Demand"] = df_forecast["AVG_WEEK"] * 4  # Assuming 1-month outlook
        forecast_fig = px.bar(df_forecast, x="BRAND", y="Projected_Demand", color="BRAND", title="Projected Demand by Brand (Next 4 Weeks)")
        st.plotly_chart(forecast_fig, use_container_width=True)

        st.subheader("🔠 ABC Inventory Classification")
        df["VALUE"] = df["PRICE"] * df["QTY_ON_HND"]
        df = df.sort_values("VALUE", ascending=False)
        df["CUM_PCT"] = df["VALUE"].cumsum() / df["VALUE"].sum()
        df["ABC_Class"] = pd.cut(df["CUM_PCT"], bins=[0, 0.7, 0.9, 1.0], labels=["A", "B", "C"])
        abc_fig = px.histogram(df, x="ABC_Class", title="ABC Inventory Analysis", color="ABC_Class")
        st.plotly_chart(abc_fig, use_container_width=True)

        st.subheader("🔍 High Margin Products")
        df["MARGIN"] = df["PRICE"] - df["COST"]
        high_margin_df = df.sort_values("MARGIN", ascending=False).head(20)
        margin_fig = px.bar(high_margin_df, x="BRAND", y="MARGIN", color="TYPE", title="Top 20 High Margin Products")
        st.plotly_chart(margin_fig, use_container_width=True)

        st.subheader("🔁 Overstocked Items")
        overstock_df = df[df["QTY_ON_HND"] > df["AVG_WEEK"] * 10]  # Define overstock threshold
        overstock_fig = px.bar(overstock_df, x="BRAND", y="QTY_ON_HND", color="TYPE", title="Overstocked Inventory")
        st.plotly_chart(overstock_fig, use_container_width=True)

        st.subheader("💤 Deadstock Detector")
        deadstock_df = df[(df["QTY_ON_HND"] > 0) & (df["WEEK_SUM"] == 0)]
        st.dataframe(deadstock_df, use_container_width=True)
else:
    st.error("❌ Failed to load the inventory file.")
