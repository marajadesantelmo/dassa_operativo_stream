import streamlit as st
import pandas as pd

# Page configurations
st.set_page_config(page_title="Monitoreo Deposito", 
                   page_icon="📊", 
                   layout="wide")

# Estilo
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load data
kpi_df = pd.read_csv('data/monitoreo/kpi.csv')
ventas_por_vendedor_df = pd.read_csv('data/monitoreo/ventas_por_vendedor.csv')
ventas_por_cliente_df = pd.read_csv('data/monitoreo/ventas_por_cliente.csv')
saldos_df = pd.read_csv('data/monitoreo/saldos.csv')

# Display data
st.title("Monitoreo Deposito")

st.header("KPIs")
st.dataframe(kpi_df, hide_index=True, use_container_width=True)

st.header("Ventas por Vendedor")
st.dataframe(ventas_por_vendedor_df, hide_index=True, use_container_width=True)

st.header("Ventas por Cliente")
st.dataframe(ventas_por_cliente_df, hide_index=True, use_container_width=True)

st.header("Saldos")
st.dataframe(saldos_df, hide_index=True, use_container_width=True)

