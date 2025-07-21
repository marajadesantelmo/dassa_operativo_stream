import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_facturacion():
    facturacion = pd.read_csv('data/facturacion_henn.csv')
    saldos = pd.read_csv('data/saldos_henn.csv')
    kpis = pd.read_csv('data/kpis.csv')
    return facturacion, saldos, kpis
    
def show_page_facturacion():
    facturacion, saldos, kpis = fetch_data_facturacion()
    saldo = kpis['Total Saldo'][kpis['Company']=='Liftvan'].sum()
    total_neto = kpis['Total Neto'][kpis['Company']=='Liftvan'].sum()
    total_importe = kpis['Total Importe'][kpis['Company']=='Liftvan'].sum()
    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.header(f"Facturación y saldos al {current_day}")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_henn.png')

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Facturación últimos 90 días")
        st.dataframe(facturacion, hide_index=True, use_container_width=True)
    with col2:
        col2_sub, col2_metric = st.columns([6, 2])
        with col2_sub:
            st.subheader("Saldos adeudados")
        with col2_metric:
            st.write(f"Saldo total: {saldo}")
        st.dataframe(saldos, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    while True:
        show_page_facturacion()
        time.sleep(60)  
        st.experimental_rerun()

