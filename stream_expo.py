import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_expo():
    arribos_expo_carga = pd.read_csv('data/arribos_expo_carga.csv')
    arribos_expo_ctns = pd.read_csv('data/arribos_expo_ctns.csv')
    verificaciones_expo = pd.read_csv('data/verificaciones_expo.csv')
    otros_expo = pd.read_csv('data/otros_expo.csv')
    remisiones = pd.read_csv('data/remisiones.csv')
    consolidados = pd.read_csv('data/consolidados.csv')
    pendiente_consolidar = pd.read_csv('data/pendiente_consolidar.csv')
    listos_para_remitir = pd.read_csv('data/listos_para_remitir.csv')
    vacios_disponibles = pd.read_csv('data/vacios_disponibles.csv')
    return arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, otros_expo, remisiones, consolidados, pendiente_consolidar, listos_para_remitir, vacios_disponibles
    
def show_page_expo():
    # Load data
    arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, otros_expo, remisiones, consolidados, pendiente_consolidar, listos_para_remitir, vacios_disponibles = fetch_data_expo()

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
        st.dataframe(arribos_expo_carga.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

    # Column 2: Pendiente Desconsolidar
    with col2:
        st.subheader("Arribos de Contenedores")
        st.dataframe(arribos_expo_ctns.style.apply(highlight, axis=1).format(precision=0), hide_index=True, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Verificaciones")
        #st.dataframe(verificaciones_expo.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)
        st.dataframe(verificaciones_expo, hide_index=True, use_container_width=True)

        st.subheader("Consolidados")
        st.dataframe(consolidados, hide_index=True, use_container_width=True)

    with col4:
        st.subheader("Remisiones")
        st.dataframe(remisiones.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)
        st.subheader("Otros")
        st.dataframe(otros_expo.style, hide_index=True, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("Estado de la carga de EXPO")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.subheader("Pendiente de Consolidar")
        st.dataframe(pendiente_consolidar, hide_index=True, use_container_width=True)
    with col5:
        st.subheader("Pendiente de Remitir")
        st.dataframe(listos_para_remitir, hide_index=True, use_container_width=True)
    with col6:
        st.subheader("Vacios Disponibles")
        st.dataframe(vacios_disponibles, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    while True:
        show_page_expo()
        time.sleep(60)  
        st.experimental_rerun() 

