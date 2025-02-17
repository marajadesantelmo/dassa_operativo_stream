import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_orden_del_dia():
    arribos = pd.read_csv('data/arribos.csv')
    arribos = arribos[arribos['Cliente'].str.contains('Mercovan')].drop(columns=['Cliente'])
    pendiente_desconsolidar = pd.read_csv('data/pendiente_desconsolidar.csv')
    pendiente_desconsolidar = pendiente_desconsolidar[pendiente_desconsolidar['Cliente'].str.contains('Mercovan')].drop(columns=['Cliente'])
    verificaciones_impo = pd.read_csv('data/verificaciones_impo.csv')
    verificaciones_impo = verificaciones_impo[verificaciones_impo['Cliente'].str.contains('Mercovan')].drop(columns=['Cliente'])
    retiros_impo = pd.read_csv('data/retiros_impo.csv')
    retiros_impo = retiros_impo[retiros_impo['Cliente'].str.contains('Mercovan')].drop(columns=['Cliente'])
    otros_impo = pd.read_csv('data/otros_impo.csv')
    otros_impo = otros_impo[otros_impo['Cliente'].str.contains('Mercovan')].drop(columns=['Cliente'])
    return arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo
    
def show_page_orden_del_dia():
    # Load data
    arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo = fetch_data_orden_del_dia()

    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.header(f"Operaciones de IMPO a partir del {current_day}")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_mercovan.png')
    col1, col2 = st.columns(2)

    col1, col2 = st.columns(2)

    with col1:
        col1_sub, col1_metric = st.columns([7, 1])
        with col1_sub:
            st.subheader("Arribos Contenedores día de hoy")
        with col1_metric:
            ctns_pendientes = arribos[(arribos['Estado'] != '-') & (~arribos['Estado'].str.contains('Arribado'))].shape[0]
            st.metric(label="CTNs pendientes", value=ctns_pendientes)
        st.dataframe(arribos.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

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

if __name__ == "__main__":
    while True:
        show_page_orden_del_dia()
        time.sleep(60)  
        st.experimental_rerun()

