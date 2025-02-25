import streamlit as st
import pandas as pd

# Page configurations
st.set_page_config(page_title="Monitoreo Deposito", 
                   page_icon="📊", 
                   layout="wide",
                   initial_sidebar_state="expanded")

# Estilo
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Custom CSS for fancy design
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
    }
    .stMetric {
        background-color: #ffffff;
        border: 1px solid #e1e1e1;
        border-radius: 10px;
        padding: 10px;
        margin: 10px;
    }
    .stDataFrame {
        background-color: #ffffff;
        border: 1px solid #e1e1e1;
        border-radius: 10px;
        padding: 10px;
        margin: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Load data
kpi_df = pd.read_csv('data/monitoreo/kpi.csv')
ventas_por_vendedor_df = pd.read_csv('data/monitoreo/ventas_por_vendedor.csv')
ventas_por_cliente_df = pd.read_csv('data/monitoreo/ventas_por_cliente.csv')
saldos_df = pd.read_csv('data/monitoreo/saldos.csv')

# Display data
st.title("Monitoreo Deposito")

st.header("KPIs")
col1, col2, col3, col4 = st.columns(4)
col1.metric(label=kpi_df.iloc[0]['Metric'], value=kpi_df.iloc[0]['Value'])
col2.metric(label=kpi_df.iloc[1]['Metric'], value=kpi_df.iloc[1]['Value'])
col3.metric(label=kpi_df.iloc[2]['Metric'], value=kpi_df.iloc[2]['Value'])
col4.metric(label=kpi_df.iloc[3]['Metric'], value=kpi_df.iloc[3]['Value'])

st.header("Ventas por Vendedor")
st.dataframe(ventas_por_vendedor_df, hide_index=True, use_container_width=True)

st.header("Ventas por Cliente")
st.dataframe(ventas_por_cliente_df, hide_index=True, use_container_width=True)

st.header("Saldos")
st.dataframe(saldos_df, hide_index=True, use_container_width=True)

