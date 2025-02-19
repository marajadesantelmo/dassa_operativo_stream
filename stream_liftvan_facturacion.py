import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_facturacion():
    facturacion = pd.read_csv('data/facturacion_liftvan.csv')
    saldos = pd.read_csv('data/saldos_liftvan.csv')
    return facturacion, saldos
    
def show_page_facturacion():
    facturacion, saldos = fetch_data_facturacion()
    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.header(f"Facturación y saldos al {current_day}")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_liftvan.png')

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Facturación últimos 90 días")
        st.dataframe(facturacion, hide_index=True, use_container_width=True)
    with col2:
        st.subheader("Saldos adeudados")
        st.dataframe(saldos, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    while True:
        show_page_facturacion()
        time.sleep(60)  
        st.experimental_rerun()

