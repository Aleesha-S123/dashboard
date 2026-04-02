import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE SETUP ---
st.set_page_config(page_title="Supply Chain Command Center", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_car_data.csv')
    df['OrderDate'] = pd.to_datetime(df['OrderDate'])
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.title("🎮 Analysis Controls")
all_makers = sorted(df['CarMaker'].unique())
selected_makers = st.sidebar.multiselect("Select Brand(s)", all_makers, default=all_makers[:10])

all_states = ["All States"] + sorted(df['State'].unique().tolist())
selected_state = st.sidebar.selectbox("Filter by State", options=all_states)

# Filter Logic
filtered_df = df[df['CarMaker'].isin(selected_makers)]
if selected_state != "All States":
    filtered_df = filtered_df[filtered_df['State'] == selected_state]

# --- MAIN DASHBOARD ---
st.title("🚗 Car Supply Chain Strategic Dashboard")
st.markdown("---")

# --- 6 KPI SECTION ---
k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Sales", f"${filtered_df['Calculated_Total'].sum():,.0f}")
k2.metric("Units Sold", f"{filtered_df['Quantity'].sum():,}")
k3.metric("Total Orders", f"{filtered_df['OrderID'].nunique():,}")
k4.metric("Avg Lead Time", f"{filtered_df['LeadTime'].mean():.1f} Days")
k5.metric("Avg Discount", f"{filtered_df['Discount'].mean()*100:.1f}%")
k6.metric("Avg Car Price", f"${filtered_df['CarPrice'].mean():,.0f}")

# --- ROW 1: SUPPLIER PERFORMANCE ---
st.divider()
st.subheader("🏭 Supplier Performance Index (Revenue vs. Efficiency)")
sup_perf = filtered_df.groupby('SupplierName').agg({'Calculated_Total': 'sum', 'LeadTime': 'mean'}).reset_index()
fig_scatter = px.scatter(sup_perf, x='LeadTime', y='Calculated_Total', size='Calculated_Total', 
                         color='LeadTime', hover_name='SupplierName', color_continuous_scale="RdYlGn_r",
                         template="plotly_white")
st.plotly_chart(fig_scatter, use_container_width=True)

# --- ROW 2: NEW REQUESTED GRAPH - AVG DELAY BY CAR MAKER ---
st.divider()
st.subheader("📊 Average Delivery Delay by Car Maker")
# Calculating the average delay per maker as shown in your uploaded figure
maker_delay = filtered_df.groupby('CarMaker')['LeadTime'].mean().reset_index().sort_values(by='LeadTime', ascending=True)
fig_maker_delay = px.bar(maker_delay, x='LeadTime', y='CarMaker', orientation='h',
                         color='LeadTime', color_continuous_scale='Reds',
                         labels={'LeadTime':'Avg Delay (Days)', 'CarMaker':'Brand'})
st.plotly_chart(fig_maker_delay, use_container_width=True)

# --- ROW 3: TOP MAKERS & DISTRIBUTION ---
st.divider()
col_maker, col_dist = st.columns(2)

with col_maker:
    st.subheader("🏆 Top 10 Car Makers by Total Sales")
    top_10 = filtered_df.groupby('CarMaker')['Calculated_Total'].sum().nlargest(10).reset_index()
    fig_maker = px.bar(top_10, x='Calculated_Total', y='CarMaker', orientation='h', color='Calculated_Total', color_continuous_scale='Viridis')
    fig_maker.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_maker, use_container_width=True)

with col_dist:
    st.subheader("📦 Lead Time Distribution by Ship Mode")
    fig_box = px.box(filtered_df, x='ShipMode', y='LeadTime', color='ShipMode')
    st.plotly_chart(fig_box, use_container_width=True)

# --- ROW 4: AVG DELAY BY SHIP MODE & FEEDBACK ---
st.divider()
col_delay, col_feedback = st.columns(2)

with col_delay:
    st.subheader("🕒 Average Delivery Delay by Shipping Method")
    delay_df = filtered_df.groupby('ShipMode')['LeadTime'].mean().reset_index().sort_values(by='LeadTime', ascending=False)
    fig_delay = px.bar(delay_df, x='ShipMode', y='LeadTime', color='LeadTime', color_continuous_scale='Reds')
    st.plotly_chart(fig_delay, use_container_width=True)

with col_feedback:
    st.subheader("🗣️ Customer Feedback Breakdown")
    fig_pie = px.pie(filtered_df, names='CustomerFeedback', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- ROW 5: TREND ---
st.divider()
st.subheader("📈 Monthly Revenue Performance")
trend = filtered_df.resample('M', on='OrderDate')['Calculated_Total'].sum().reset_index()
st.line_chart(trend.set_index('OrderDate'))

# --- EXECUTIVE SUMMARY ---
st.divider()
st.header("🎯 Competition Insights")
with st.container(border=True):
    ans1, ans2, ans3 = st.columns(3)
    with ans1:
        st.success("**Top Performer:** " + df.groupby('CarMaker')['Calculated_Total'].sum().idxmax())
    with ans2:
        st.warning("**Fastest Logistics:** " + df.groupby('ShipMode')['LeadTime'].mean().idxmin())
    with ans3:
        st.error("**Strategic Priority:** Speed Optimization")

st.caption("Dashboard developed for Supply Chain Competition 2026.")
