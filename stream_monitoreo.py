import streamlit as st
import pandas as pd

# Page configurations
st.set_page_config(page_title="Monitoreo", 
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
existente_df = pd.read_csv('data/monitoreo/existente.csv')
resumen_mensual_ctns_df = pd.read_csv('data/monitoreo/resumen_mensual_ctns.csv')
kpi_data_expo= pd.read_csv('data/monitoreo/kpi_data_expo.csv')
kpi_data_impo= pd.read_csv('data/monitoreo/kpi_data_impo.csv')


# Display data
st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://raw.githubusercontent.com/marajadesantelmo/dassa_operativo_stream/main/logo_mini.png" style="width: 50px; margin-right: 10px;">
        <h1 style="margin: 0;">Monitoreo</h1>
    </div>
    """,
    unsafe_allow_html=True
)

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

st.subheader("Ventas por Vendedor")
st.dataframe(ventas_por_vendedor_df, hide_index=True, use_container_width=True)

st.subheader("Ventas por Cliente")
st.dataframe(ventas_por_cliente_df, hide_index=True, use_container_width=True)

st.subheader("Saldos")
st.dataframe(saldos_df, hide_index=True, use_container_width=True)

st.header("Existente")

col1, col2 = st.columns(2)
col1.metric(label=existente_df.iloc[0]['Metricas'], value=existente_df.iloc[0]['Valores'])
col2.metric(label=existente_df.iloc[1]['Metricas'], value=existente_df.iloc[1]['Valores'])

st.header("CTNs IMPO ingresados")

col1, col2 = st.columns(2)
col1.metric(label="Mes actual", value=kpi_data_impo.iloc[0]['Mes actual'])
col2.metric(label="Mes anterior", value=kpi_data_impo.iloc[0]['Mes anterior'])

col3, col4 = st.columns(2)
col3.metric(label="Promedio mensual", value=kpi_data_impo.iloc[0]['Promedio mensual'])
col4.metric(label="Proyeccion mes actual", value=kpi_data_impo.iloc[0]['Proyeccion mes actual'])

st.header("CTNs EXPO egresados")

col1, col2 = st.columns(2)
col1.metric(label="Mes actual", value=kpi_data_expo.iloc[0]['Mes actual'])
col2.metric(label="Mes anterior", value=kpi_data_expo.iloc[0]['Mes anterior'])

col3, col4 = st.columns(2)
col3.metric(label="Promedio mensual", value=kpi_data_expo.iloc[0]['Promedio mensual'])
col4.metric(label="Proyeccion mes actual", value=kpi_data_expo.iloc[0]['Proyeccion mes actual'])