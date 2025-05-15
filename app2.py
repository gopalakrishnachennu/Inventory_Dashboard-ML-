import streamlit as st
import pandas as pd
import plotly.express as px
from inventory_manager import main  # Load processed inventory data

st.set_page_config(page_title="📈 Inventory Visual Analytics", layout="wide")
st.title("📊 Inventory Visual Analytics")

df = main()

if not df.empty:
    st.sidebar.header("🔍 Filter Options")

    # Optional filters by Brand and Type for targeted visualizations
    selected_brand = st.sidebar.selectbox("Select Brand:", ["All"] + sorted(df["BRAND"].dropna().unique().tolist()))
    if selected_brand != "All":
        df = df[df["BRAND"] == selected_brand]

    selected_type = st.sidebar.selectbox("Select Type:", ["All"] + sorted(df["TYPE"].dropna().unique().tolist()))
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
    st.warning("Inventory data could not be loaded for visualization.")
