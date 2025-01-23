import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_expo():
    arribos_expo_carga = pd.read_csv('data/arribos_expo_carga.csv')
    arribos_expo_carga = arribos_expo_carga[arribos_expo_carga['Cliente']=='Grupo Simpa Sa']
    arribos_expo_ctns = pd.read_csv('data/arribos_expo_ctns.csv')
    arribos_expo_ctns = arribos_expo_ctns[arribos_expo_ctns['Cliente']=='Grupo Simpa Sa']
    verificaciones_expo = pd.read_csv('data/verificaciones_expo.csv')
    verificaciones_expo = verificaciones_expo[verificaciones_expo['Cliente']=='Grupo Simpa Sa']
    otros_expo = pd.read_csv('data/otros_expo.csv')
    otros_expo = otros_expo[otros_expo['Cliente']=='Grupo Simpa Sa']
    remisiones = pd.read_csv('data/remisiones.csv')
    remisiones = remisiones[remisiones['Cliente']=='Grupo Simpa Sa']
    consolidados = pd.read_csv('data/consolidados.csv')
    consolidados = consolidados[consolidados['Cliente']=='Grupo Simpa Sa']
    pendiente_consolidar = pd.read_csv('data/pendiente_consolidar.csv')
    pendiente_consolidar = pendiente_consolidar[pendiente_consolidar['Cliente']=='Grupo Simpa Sa']
    listos_para_remitir = pd.read_csv('data/listos_para_remitir.csv')
    listos_para_remitir = listos_para_remitir[listos_para_remitir['Cliente']=='Grupo Simpa Sa']
    vacios_disponibles = pd.read_csv('data/vacios_disponibles.csv')
    vacios_disponibles = vacios_disponibles[vacios_disponibles['Cliente']=='Grupo Simpa Sa']
    return arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, otros_expo, remisiones, consolidados, pendiente_consolidar, listos_para_remitir, vacios_disponibles
    
def show_page_expo():
    # Load data
    arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, otros_expo, remisiones, consolidados, pendiente_consolidar, listos_para_remitir, vacios_disponibles = fetch_data_expo()

    col_logo, col_title, col_simpa = st.columns([1, 5, 1])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Operaciones de IMPO a partir del {current_day}")
    with col_simpa:
        st.image('logo_simpa.png')


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
        st.dataframe(verificaciones_expo.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

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

