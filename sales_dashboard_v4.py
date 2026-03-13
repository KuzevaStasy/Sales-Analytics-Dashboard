import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# PAGE CONFIG
st.set_page_config(page_title="Sales Analytics Dashboard", layout="wide")

# LOAD DATA
df = pd.read_excel("sales_data.xlsx")

st.title("Sales Analytics Dashboard")

# ======================
# SIDEBAR FILTERS
# ======================

st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Region",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

category = st.sidebar.multiselect(
    "Product Category",
    options=df["Product_Category"].unique(),
    default=df["Product_Category"].unique()
)

customer = st.sidebar.multiselect(
    "Customer Type",
    options=df["Customer_Type"].unique(),
    default=df["Customer_Type"].unique()
)

channel = st.sidebar.multiselect(
    "Sales Channel",
    options=df["Sales_Channel"].unique(),
    default=df["Sales_Channel"].unique()
)

# ======================
# FILTER DATA
# ======================

df_filtered = df[
    (df["Region"].isin(region)) &
    (df["Product_Category"].isin(category)) &
    (df["Customer_Type"].isin(customer)) &
    (df["Sales_Channel"].isin(channel))
].copy()

# ======================
# CALCULATIONS
# ======================

df_filtered["Revenue"] = df_filtered["Unit_Price"] * df_filtered["Quantity_Sold"]

df_filtered["Cost"] = df_filtered["Unit_Cost"] * df_filtered["Quantity_Sold"]

df_filtered["Profit"] = df_filtered["Revenue"] - df_filtered["Cost"]

total_revenue = df_filtered["Revenue"].sum()
total_units = df_filtered["Quantity_Sold"].sum()
avg_discount = df_filtered["Discount"].mean()
total_profit = df_filtered["Profit"].sum()

profit_margin = total_profit / total_revenue if total_revenue > 0 else 0

# ======================
# KPI ROW
# ======================

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Revenue", f"${total_revenue:,.0f}")
k2.metric("Units Sold", f"{total_units:,}")
k3.metric("Avg Discount", f"{avg_discount:.2%}")
k4.metric("Profit", f"${total_profit:,.0f}")
k5.metric("Profit Margin", f"{profit_margin:.2%}")

st.markdown("---")

# ======================
# REVENUE BY REGION
# ======================

fig_region = px.bar(
    df_filtered.groupby("Region")["Revenue"].sum().reset_index(),
    x="Region",
    y="Revenue",
    title="Revenue by Region"
)

# ======================
# PRODUCT CATEGORY
# ======================

fig_product = px.pie(
    df_filtered,
    names="Product_Category",
    values="Revenue",
    title="Revenue by Product Category"
)

# ======================
# SALES CHANNEL
# ======================

fig_channel = px.bar(
    df_filtered.groupby("Sales_Channel")["Revenue"].sum().reset_index(),
    x="Sales_Channel",
    y="Revenue",
    title="Revenue by Sales Channel"
)

# ======================
# CUSTOMER TYPE
# ======================

fig_customer = px.bar(
    df_filtered.groupby("Customer_Type")["Revenue"].sum().reset_index(),
    x="Customer_Type",
    y="Revenue",
    title="Revenue by Customer Type"
)

# ======================
# TOP SALES REPS
# ======================

sales_rep = df_filtered.groupby("Sales_Rep")["Revenue"].sum().reset_index()

fig_sales_rep = px.bar(
    sales_rep.sort_values("Revenue", ascending=False).head(10),
    x="Revenue",
    y="Sales_Rep",
    orientation="h",
    title="Top Sales Representatives"
)

# ======================
# SALES TREND
# ======================

df_filtered["Sale_Date"] = pd.to_datetime(df_filtered["Sale_Date"])

sales_trend = df_filtered.groupby(
    df_filtered["Sale_Date"].dt.to_period("M")
)["Revenue"].sum().reset_index()

sales_trend["Sale_Date"] = sales_trend["Sale_Date"].astype(str)

fig_trend = px.line(
    sales_trend,
    x="Sale_Date",
    y="Revenue",
    title="Monthly Revenue Trend"
)

# ======================
# FORECAST
# ======================

sales_trend["Month_Index"] = np.arange(len(sales_trend))

coeffs = np.polyfit(
    sales_trend["Month_Index"],
    sales_trend["Revenue"],
    1
)

trendline = np.poly1d(coeffs)

sales_trend["Forecast"] = trendline(sales_trend["Month_Index"])

fig_forecast = px.line(
    sales_trend,
    x="Sale_Date",
    y=["Revenue", "Forecast"],
    title="Revenue Forecast"
)

# ======================
# HEATMAP
# ======================

heatmap_data = df_filtered.pivot_table(
    values="Revenue",
    index="Region",
    columns="Product_Category",
    aggfunc="sum"
)

fig_heatmap = px.imshow(
    heatmap_data,
    text_auto=True,
    aspect="auto",
    title="Sales Heatmap (Region vs Product)"
)

# ======================
# DASHBOARD LAYOUT
# ======================

row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.plotly_chart(fig_region, use_container_width=True)

with row1_col2:
    st.plotly_chart(fig_product, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.plotly_chart(fig_channel, use_container_width=True)

with row2_col2:
    st.plotly_chart(fig_customer, use_container_width=True)

row3_col1, row3_col2 = st.columns(2)

with row3_col1:
    st.plotly_chart(fig_sales_rep, use_container_width=True)

with row3_col2:
    st.plotly_chart(fig_trend, use_container_width=True)

row4_col1, row4_col2 = st.columns(2)

with row4_col1:
    st.plotly_chart(fig_forecast, use_container_width=True)

with row4_col2:
    st.plotly_chart(fig_heatmap, use_container_width=True)