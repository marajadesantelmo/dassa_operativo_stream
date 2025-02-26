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
ventas_clientes_nuevos = pd.read_csv('data/monitoreo/ventas_clientes_nuevos.csv')
ventas_totales_por_mes_tabla = pd.read_csv('data/monitoreo/ventas_totales_por_mes_tabla.csv')
ventas_totales_por_mes_grafico = pd.read_csv('data/monitoreo/ventas_totales_por_mes_grafico.csv')


# Display data
st.markdown(
    """
    <div style="display: flex; align-items: center;">
        <img src="https://raw.githubusercontent.com/marajadesantelmo/dassa_operativo_stream/main/logo_mini.png" style="width: 50px; margin-right: 10px;">
        <h1 style="margin: 0;">Ventas</h1>
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

st.markdown("<hr>", unsafe_allow_html=True)

st.subheader("Ventas por Vendedor")
st.dataframe(ventas_por_vendedor_df, hide_index=True, use_container_width=True)

st.subheader("Ventas por Cliente")
st.dataframe(ventas_por_cliente_df, hide_index=True, use_container_width=True)

st.subheader("Ventas a Clientes Nuevos")
st.dataframe(ventas_clientes_nuevos, hide_index=True, use_container_width=True)

st.subheader("Ventas totales por mes")
st.bar_chart(ventas_totales_por_mes_grafico.set_index('Mes'))
st.dataframe(ventas_totales_por_mes_tabla, hide_index=True, use_container_width=True)

st.subheader("Saldos")
st.dataframe(saldos_df, hide_index=True, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)
