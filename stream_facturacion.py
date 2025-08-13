import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import filter_dataframe_by_clients
from supabase_connection import fetch_table_data

def fetch_data_facturacion():
    facturacion = fetch_table_data("facturacion")
    facturacion.drop(columns=['id'], inplace=True, errors='ignore')
    saldos = fetch_table_data("saldos")
    saldos.drop(columns=['id'], inplace=True, errors='ignore')
    return facturacion, saldos
    
def show_page_facturacion(allowed_clients=None):
    facturacion, saldos, = fetch_data_facturacion()
    if allowed_clients:
        facturacion = filter_dataframe_by_clients(facturacion, allowed_clients)
        saldos = filter_dataframe_by_clients(saldos, allowed_clients)
    
    total_neto = facturacion['neto_numerico'].sum()
    importe_total = facturacion['total_numerico'].sum()
    saldos['saldo_numerico'] = saldos['saldo_numerico'].astype(float)
    total_saldo = saldos['saldo_numerico'].sum()

    col_title, col_logo = st.columns([5, 1])
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.header(f"Facturación y saldos al {current_day}")
    with col_logo:
        st.image('logo.png')


    col1, col2 = st.columns(2)
    with col1:
        col1_sub, col1_metric = st.columns([6, 2])
        with col1_sub:
            st.subheader("Facturación últimos 90 días")
        with col1_metric:
            st.write(f"Neto: ${total_neto:,.0f}    Total:  ${importe_total:,.0f}".replace(",", "."))
        st.dataframe(facturacion, hide_index=True, use_container_width=True)
    with col2:
        col2_sub, col2_metric = st.columns([6, 2])
        with col2_sub:
            st.subheader("Saldos adeudados")
        with col2_metric:
            st.write(f"Saldo total: ${total_saldo:,.0f}".replace(",", "."))
        st.dataframe(saldos, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    while True:
        show_page_facturacion()
        time.sleep(60)  
        st.experimental_rerun()

