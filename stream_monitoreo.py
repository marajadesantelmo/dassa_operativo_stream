import streamlit as st
import pandas as pd

# Page configurations
st.set_page_config(page_title="Monitoreo Deposito", 
                   page_icon="📊", 
                   layout="wide")

# Estilo
with open("styles_mobile.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load data
kpi_df = pd.read_csv('data/monitoreo/kpi.csv')
ventas_por_vendedor_df = pd.read_csv('data/monitoreo/ventas_por_vendedor.csv')
ventas_por_cliente_df = pd.read_csv('data/monitoreo/ventas_por_cliente.csv')
saldos_df = pd.read_csv('data/monitoreo/saldos.csv')

# Display data
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("logo_mini.png", use_column_width=True)
with col_title:
    st.title("Monitoreo")

st.header("KPIs")
col1, col2 = st.columns(2)
col1.metric(label=kpi_df.iloc[0]['Metric'], value=kpi_df.iloc[0]['Value'])
col2.metric(label=kpi_df.iloc[1]['Metric'], value=kpi_df.iloc[1]['Value'])

col3, col4 = st.columns(2)
col3.metric(label=kpi_df.iloc[2]['Metric'], value=kpi_df.iloc[2]['Value'])
col4.metric(label=kpi_df.iloc[3]['Metric'], value=kpi_df.iloc[3]['Value'])

# Adjust font size for mobile view
st.markdown("""
    <style>
    .stMetric {
        font-size: calc(1em + 1vw);
    }
    </style>
    """, unsafe_allow_html=True)

st.header("Ventas por Vendedor")
st.dataframe(ventas_por_vendedor_df, hide_index=True, use_container_width=True)

st.header("Ventas por Cliente")
st.dataframe(ventas_por_cliente_df, hide_index=True, use_container_width=True)

st.header("Saldos")
st.dataframe(saldos_df, hide_index=True, use_container_width=True)

