import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight, rellenar_df_vacio

def fetch_data_expo():
    arribos_expo_carga = pd.read_csv('data/arribos_expo_carga.csv')
    arribos_expo_ctns = pd.read_csv('data/arribos_expo_ctns.csv')
    verificaciones_expo = pd.read_csv('data/verificaciones_expo.csv')
    retiros_expo = pd.read_csv('data/retiros_expo.csv')
    otros_expo = pd.read_csv('data/otros_expo.csv')
    remisiones = pd.read_csv('data/remisiones.csv')
    consolidados = pd.read_csv('data/consolidados.csv')
    return arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, retiros_expo, otros_expo, remisiones, consolidados
    

def show_page_expo():
    # Load data
    arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, retiros_expo, otros_expo, remisiones, consolidados = fetch_data_expo()

    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Operaciones de EXPO a partir del {current_day}")

    # Create two columns
    col1, col2 = st.columns(2)

    # Column 1: Arribos
    with col1:
        st.subheader("Arribos de Carga")
        st.dataframe(arribos_expo_carga.style.apply(highlight, axis=1), hide_index=True)

    # Column 2: Pendiente Desconsolidar
    with col2:
        st.subheader("Arribos de Contenedores")
        st.dataframe(arribos_expo_ctns.style.apply(highlight, axis=1).format(precision=0), hide_index=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Verificaciones")
        st.dataframe(verificaciones_expo, hide_index=True)

        st.subheader("Otros Exportaciones")
        st.dataframe(otros_expo, hide_index=True)

    with col4:
        st.subheader("Retiros")
        st.dataframe(retiros_expo.style.apply(highlight, axis=1), hide_index=True)

        st.subheader("Remisiones")
        st.dataframe(remisiones.style.apply(highlight, axis=1), hide_index=True)

        st.subheader("Consolidados")
        st.dataframe(consolidados, hide_index=True)

if __name__ == "__main__":
    while True:
        show_page_expo()
        time.sleep(60)  
        st.experimental_rerun() 

