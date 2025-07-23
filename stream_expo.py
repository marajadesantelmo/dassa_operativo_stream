import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight
from supabase_connection import fetch_table_data

def fetch_data_expo():
    arribos_expo_carga = fetch_table_data("arribos_expo_carga")
    arribos_expo_carga['Fecha'] = pd.to_datetime(arribos_expo_carga['Fecha'], format='%d/%m')
    arribos_expo_carga = arribos_expo_carga.sort_values(by="Fecha")
    arribos_expo_carga['Fecha'] = arribos_expo_carga['Fecha'].dt.strftime('%d/%m')
    arribos_expo_ctns = fetch_table_data("arribos_expo_ctns")
    arribos_expo_ctns['Fecha'] = pd.to_datetime(arribos_expo_ctns['Fecha'], format='%d/%m')
    arribos_expo_ctns = arribos_expo_ctns.sort_values(by="Fecha")
    arribos_expo_ctns['Fecha'] = arribos_expo_ctns['Fecha'].dt.strftime('%d/%m')
    verificaciones_expo = fetch_table_data("verificaciones_expo")
    verificaciones_expo = verificaciones_expo[verificaciones_expo['Dia'] != '-']
    otros_expo = fetch_table_data("otros_expo")
    otros_expo = otros_expo[otros_expo['Dia'] != '-']
    remisiones = fetch_table_data("remisiones")
    # Filtro para eliminar filas con 'Dia' igual a '-'
    remisiones = remisiones[remisiones['Dia'] != '-']
    if not remisiones.empty:
        remisiones['Dia'] = pd.to_datetime(remisiones['Dia'], format='%d/%m', errors='coerce')
        remisiones['Hora'] = pd.to_datetime(remisiones['Hora'], errors='coerce').dt.strftime('%H:%M')
        # Remove rows where date conversion failed
        remisiones = remisiones.dropna(subset=['Dia'])
        remisiones.sort_values(by=['Dia', 'Hora'], inplace=True)
        remisiones['Hora'] = remisiones['Hora'].astype(str).str[:5]
        remisiones['Hora'] = remisiones['Hora'].apply(lambda x: x[1:] if isinstance(x, str) and x.startswith('0') else x)
        remisiones['Dia'] = remisiones['Dia'].dt.strftime('%d/%m')
        remisiones['Volumen'] = remisiones['Volumen'].round(0).astype(int)
        cols = remisiones.columns.tolist()
        cols.insert(1, cols.pop(cols.index('Hora')))
        remisiones = remisiones[cols]
    pendiente_consolidar = fetch_table_data("pendiente_consolidar")
    listos_para_remitir = fetch_table_data("listos_para_remitir")
    vacios_disponibles = fetch_table_data("vacios_disponibles")
    a_consolidar = fetch_table_data("a_consolidar")
    a_consolidar.sort_values(by="Dias", ascending=False, inplace=True)
    return arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, otros_expo, remisiones, pendiente_consolidar, listos_para_remitir, vacios_disponibles, a_consolidar

@st.cache_data(ttl=60)
def fetch_last_update():
    update_log = fetch_table_data("update_log")
    if not update_log.empty:
        last_update = update_log[update_log['table_name'] == 'Arribos y existente']['last_update'].max()
        return pd.to_datetime(last_update).strftime("%d/%m/%Y %H:%M")
    return "No disponible"

    

def show_page_expo():
    # Load data
    arribos_expo_carga, arribos_expo_ctns, verificaciones_expo, otros_expo, remisiones, pendiente_consolidar, listos_para_remitir, vacios_disponibles, a_consolidar = fetch_data_expo()
    last_update = fetch_last_update()
    mudanceras_filter = ['Mercovan', 'Lift Van', 'Rsm', 'Fenisan', 'Moniport', 'Bymar', 'Noah']
    if st.session_state['username'] == "mudancera":
        arribos_expo_carga = arribos_expo_carga[arribos_expo_carga['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        arribos_expo_ctns = arribos_expo_ctns[arribos_expo_ctns['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        verificaciones_expo = verificaciones_expo[verificaciones_expo['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        otros_expo = otros_expo[otros_expo['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        remisiones = remisiones[remisiones['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        pendiente_consolidar = pendiente_consolidar[pendiente_consolidar['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        listos_para_remitir = listos_para_remitir[listos_para_remitir['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        vacios_disponibles = vacios_disponibles[vacios_disponibles['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        a_consolidar = a_consolidar[a_consolidar['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        

    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
        st.info(f'Última actualización: {last_update}')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Operaciones de EXPO a partir del {current_day}")

    
    col1, col2 = st.columns(2)
    with col1:
        col1_sub, col1_metric, col1_metric2 = st.columns([6, 1, 1])
        with col1_sub:
            st.subheader("Arribos de Carga")
        with col1_metric:
            # Get today's date in DD/MM format
            today = datetime.now().strftime("%d/%m")
            carga_pendientes = arribos_expo_carga[(arribos_expo_carga['Estado'] == 'Pendiente') & 
                                                 (arribos_expo_carga['Fecha'] == today)].shape[0]
            st.metric(label="Pendientes hoy", value=carga_pendientes)
        with col1_metric2:
            carga_arribada = arribos_expo_carga[(arribos_expo_carga['Estado'].str.contains('Arribado'))].shape[0]
            st.metric(label="Arribados", value=carga_arribada)
        st.dataframe(arribos_expo_carga.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

    with col2:
        co2_sub, col2_metric1, col2_metric2 = st.columns([6, 1, 1])
        with co2_sub:
            st.subheader("Arribos de Contenedores")
        with col2_metric1:
            st.metric(label="Pendientes hoy", value=arribos_expo_ctns[(arribos_expo_ctns['Estado'] == 'Pendiente') & 
                                                 (arribos_expo_ctns['Fecha'] == today)]['Cantidad'].sum())
        with col2_metric2:
            st.metric(label="Arribados", value=arribos_expo_ctns[(arribos_expo_ctns['Estado'].str.contains('Arribado'))].shape[0])
        st.dataframe(arribos_expo_ctns.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)


    col3, col4 = st.columns(2)
    with col3:
        col3_sub, col3_metric = st.columns([7, 1])
        with col3_sub:
            st.subheader("Pendiente de Consolidar")
        with col3_metric:
            st.metric(label="Pendientes", value=a_consolidar.shape[0])
        st.dataframe(a_consolidar, 
                    column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",)} ,
                    hide_index=True, use_container_width=True)
        if st.session_state['username'] != "plazoleta" and not verificaciones_expo.empty:
            st.subheader("Verificaciones")
            st.dataframe(verificaciones_expo.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

    with col4:
        col4_sub, col4_metric, col4_metric2 = st.columns([7, 1, 1])
        with col4_sub:
            st.subheader("Remisiones")
        with col4_metric:
            remisiones_pendientes = remisiones[(remisiones['Estado'] == 'Pendiente') & 
                                                 (remisiones['Dia'] == today)].shape[0]
            st.metric(label="Pendientes hoy", value=remisiones_pendientes)
        with col4_metric2:
            remisiones_realizadas= remisiones[(remisiones['Estado'].str.contains('Realizado'))].shape[0]
            st.metric(label="Realizadas", value=remisiones_realizadas)
        st.dataframe(remisiones.style.apply(highlight, axis=1), 
                     column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",)} ,
                     hide_index=True, use_container_width=True)
        if st.session_state['username'] != "plazoleta" and not otros_expo.empty:
            st.subheader("Otros")
            st.dataframe(otros_expo.style, hide_index=True, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("Estado de la carga de EXPO")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.subheader("Carga en Stock")
        st.dataframe(pendiente_consolidar, hide_index=True, use_container_width=True)
    with col5:
        st.subheader("Pendiente de Remitir")
        st.dataframe(listos_para_remitir, 
                    column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",)},
                    hide_index=True, use_container_width=True)
    with col6:
        st.subheader("Vacios Disponibles")
        st.dataframe(vacios_disponibles, hide_index=True, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

if __name__ == "__main__":
    while True:
        show_page_expo()
        time.sleep(60)  
        st.experimental_rerun()

