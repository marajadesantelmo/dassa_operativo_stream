import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight

@st.cache_data(ttl=60) 
def fetch_data_tele():
    arribos = pd.read_csv('data/arribos.csv')
    pendiente_desconsolidar = pd.read_csv('data/pendiente_desconsolidar.csv')
    verificaciones_impo = pd.read_csv('data/verificaciones_impo.csv')
    retiros_impo = pd.read_csv('data/retiros_impo.csv')
    otros_impo = pd.read_csv('data/otros_impo.csv')
    arribos_expo_carga = pd.read_csv('data/arribos_expo_carga.csv')
    arribos_expo_ctns = pd.read_csv('data/arribos_expo_ctns.csv')
    verificaciones_expo = pd.read_csv('data/verificaciones_expo.csv')
    otros_expo = pd.read_csv('data/otros_expo.csv')
    remisiones = pd.read_csv('data/remisiones.csv')
    consolidados = pd.read_csv('data/consolidados.csv')
    return arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo, arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, otros_expo, remisiones, consolidados, pendiente_consolidar, listos_para_remitir, vacios_disponibles

def show_page_impo():
    # Load data
    arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo,  arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, otros_expo, remisiones, consolidados, pendiente_consolidar, listos_para_remitir, vacios_disponibles= fetch_data_tele()

    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Operaciones de IMPO a partir del {current_day}")

    col1, col2 = st.columns(2)

    with col1:
        col1_sub, col1_metric = st.columns([7, 1])
        with col1_sub:
            st.subheader("Arribos Contenedores día de hoy")
        with col1_metric:
            ctns_pendientes = arribos[(arribos['Estado'] != '-') & (~arribos['Estado'].str.contains('Arribado'))].shape[0]
            st.metric(label="CTNs pendientes", value=ctns_pendientes)
        st.dataframe(arribos.style.apply(highlight, axis=1).set_properties(subset=['Cliente'], **{'width': '20px'}), hide_index=True, use_container_width=True)

    with col2:
        col2_sub, col2_metric1, col2_mentric2 = st.columns([6, 1, 1])
        with col2_sub:
            st.subheader("Pendiente Desconsolidar y Vacios")
        with col2_metric1:
            st.metric(label="Ptes. Desco.", value=pendiente_desconsolidar[pendiente_desconsolidar['Estado'] == 'Pte. Desc.'].shape[0])
        with col2_mentric2:
            st.metric(label="Vacios", value=pendiente_desconsolidar[pendiente_desconsolidar['Estado'] == 'Vacio'].shape[0])
        st.dataframe(pendiente_desconsolidar.style.apply(highlight, axis=1).format(precision=0), hide_index=True, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Verificaciones")
        st.dataframe(verificaciones_impo.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)
        st.subheader("Otros")
        st.dataframe(otros_impo.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

    with col4:
        st.subheader("Retiros")
        st.dataframe(retiros_impo.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)


# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_impo()
        time.sleep(60)  
        st.experimental_rerun() 

