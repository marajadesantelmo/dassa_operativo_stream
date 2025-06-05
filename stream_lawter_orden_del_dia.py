import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_orden_del_dia():
    arribos_expo_carga = pd.read_csv('data/arribos_expo_carga.csv')
    arribos_expo_carga = arribos_expo_carga[arribos_expo_carga['Cliente']== 'Lawter Argentina S.A.'].drop(columns=['Cliente'])
    arribos_expo_ctns = pd.read_csv('data/arribos_expo_ctns.csv')
    arribos_expo_ctns = arribos_expo_ctns[arribos_expo_ctns['Cliente']== 'Lawter Argentina S.A.'].drop(columns=['Cliente'])
    verificaciones_expo = pd.read_csv('data/verificaciones_expo.csv')
    verificaciones_expo = verificaciones_expo[verificaciones_expo['Cliente']== 'Lawter Argentina S.A.'].drop(columns=['Cliente'])
    otros_expo = pd.read_csv('data/otros_expo.csv')
    otros_expo = otros_expo[otros_expo['Cliente']== 'Lawter Argentina S.A.'].drop(columns=['Cliente'])
    remisiones = pd.read_csv('data/remisiones.csv')
    remisiones = remisiones[remisiones['Cliente']== 'Lawter Argentina S.A.'].drop(columns=['Cliente'])
    pendiente_consolidar = pd.read_csv('data/pendiente_consolidar.csv')
    pendiente_consolidar = pendiente_consolidar[pendiente_consolidar['Cliente']== 'Lawter Argentina S.A.'].drop(columns=['Cliente'])
    listos_para_remitir = pd.read_csv('data/listos_para_remitir.csv')
    listos_para_remitir = listos_para_remitir[listos_para_remitir['Cliente']== 'Lawter Argentina S.A.'].drop(columns=['Cliente'])
    return  arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, otros_expo, remisiones, pendiente_consolidar, listos_para_remitir
    
def show_page_orden_del_dia():
    # Load data
    arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, otros_expo, remisiones, pendiente_consolidar, listos_para_remitir = fetch_data_orden_del_dia()

    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.header(f"Operaciones de EXPO a partir del {current_day}")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_lawter.png')
    col1, col2 = st.columns(2)


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

    with col4:
        st.subheader("Remisiones")
        st.dataframe(remisiones.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)
        st.subheader("Otros")
        st.dataframe(otros_expo.style, hide_index=True, use_container_width=True)

    
    st.header("Estado de la carga de EXPO")
    col4, col5 = st.columns(2)
    with col4:
        st.subheader("Pendiente de Consolidar")
        st.dataframe(pendiente_consolidar, hide_index=True, use_container_width=True)
    with col5:
        st.subheader("Pendiente de Remitir")
        st.dataframe(listos_para_remitir, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    while True:
        show_page_orden_del_dia()
        time.sleep(60)  
        st.experimental_rerun()

