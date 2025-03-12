import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_facturacion():
    facturacion = pd.read_csv('data/facturacion_global_comex.csv')
    facturacion_clientes = pd.read_csv('data/facturacion_global_comex_clientes.csv')
    saldos = pd.read_csv('data/saldos_global_comex.csv')
    saldos_clientes = pd.read_csv('data/saldos_global_comex_clientes.csv')
    kpis = pd.read_csv('data/kpis.csv')
    return facturacion, saldos, kpis, facturacion_clientes, saldos_clientes
    
def show_page_facturacion():
    facturacion, saldos, kpis, facturacion_clientes, saldos_clientes = fetch_data_facturacion()
    saldo = kpis['Total Saldo'][kpis['Company']=='Global Comex'].sum()
    total_neto = kpis['Total Neto'][kpis['Company']=='Global Comex'].sum()
    total_importe = kpis['Total Importe'][kpis['Company']=='Global Comex'].sum()
    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.header(f"Facturación y saldos al {current_day}")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_global_comex.png')

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Facturación últimos 90 días")
        st.dataframe(facturacion, hide_index=True, use_container_width=True)
        st.write(f"Total Neto: {total_neto}  |  Total Importe: {total_importe}")

    with col2:
        st.subheader("Saldos adeudados")
        st.dataframe(saldos, hide_index=True, use_container_width=True)
        st.write(f"Saldo total: {saldo}")

    st.subheader("Información agregada por Razón Social")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Facturación últimos 90 días")
        st.dataframe(facturacion_clientes, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Saldos adeudados")
        st.dataframe(saldos_clientes, hide_index=True, use_container_width=True)
if __name__ == "__main__":
    while True:
        show_page_facturacion()
        time.sleep(60)  
        st.experimental_rerun()

