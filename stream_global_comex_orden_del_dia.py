import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_orden_del_dia():
    clientes_global_comex = pd.read_csv('data/clientes_global_comex.csv')
    clientes_global_comex = clientes_global_comex['apellido'].tolist()
    arribos = pd.read_csv('data/arribos.csv')
    arribos = arribos[arribos['Cliente'].isin(clientes_global_comex)]
    pendiente_desconsolidar = pd.read_csv('data/pendiente_desconsolidar.csv')
    pendiente_desconsolidar = pendiente_desconsolidar[pendiente_desconsolidar['Cliente'].isin(clientes_global_comex)]
    verificaciones_impo = pd.read_csv('data/verificaciones_impo.csv')
    verificaciones_impo = verificaciones_impo[verificaciones_impo['Cliente'].isin(clientes_global_comex)]
    retiros_impo = pd.read_csv('data/retiros_impo.csv')
    retiros_impo = retiros_impo[retiros_impo['Cliente'].isin(clientes_global_comex)]
    retiros_impo['e-tally'] = retiros_impo['e-tally'].fillna("")
    otros_impo = pd.read_csv('data/otros_impo.csv')
    otros_impo = otros_impo[otros_impo['Cliente'].isin(clientes_global_comex)]
    remisiones = pd.read_csv('data/remisiones.csv')
    remisiones = remisiones[remisiones['Cliente'].isin(clientes_global_comex)]
    existente_plz = pd.read_csv('data/existente_plz.csv')
    existente_plz = existente_plz[existente_plz['Cliente'].isin(clientes_global_comex)]
    existente_plz.drop(columns=['e-tally'], inplace=True)
    existente_alm = pd.read_csv('data/existente_alm.csv')
    existente_alm = existente_alm[existente_alm['Cliente'].isin(clientes_global_comex)]
    existente_plz = existente_plz.drop_duplicates()
    existente_alm = existente_alm.drop_duplicates()
    return arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo, existente_alm, existente_plz
    
def show_page_orden_del_dia():
    # Load data
    arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo, existente_alm, existente_plz = fetch_data_orden_del_dia()

    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.header(f"Operaciones de IMPO a partir del {current_day}")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_global_comex.png')
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
        st.dataframe(retiros_impo.style.apply(highlight, axis=1), 
                    column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",)},
                    hide_index=True, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader(f"Estado de la carga de IMPO")
    col4, col5 = st.columns(2)
    with col4:
        st.subheader("Plazoleta")
        st.dataframe(existente_plz, hide_index=True, use_container_width=True)
    with col5:
        st.subheader("Almacen")
        st.dataframe(existente_alm, 
                     column_config={'e-tally': st.column_config.LinkColumn('e-tally link', 
                                                                          display_text='\U0001F517',)},
                     hide_index=True, use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)

if __name__ == "__main__":
    while True:
        show_page_orden_del_dia()
        time.sleep(60)  
        st.experimental_rerun()

