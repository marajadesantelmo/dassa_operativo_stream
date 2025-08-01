import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight
from supabase_connection import fetch_table_data, insert_data

@st.cache_data(ttl=60) 

def fetch_data_trafico():
    arribos = fetch_table_data("arribos")
    arribos = arribos.sort_values(by="Turno")
    pendiente_desconsolidar = fetch_table_data("pendiente_desconsolidar")
    arribos_expo_ctns = fetch_table_data("arribos_expo_ctns")  
    arribos_expo_ctns['Fecha'] = pd.to_datetime(arribos_expo_ctns['Fecha'], format='%d/%m')
    arribos_expo_ctns = arribos_expo_ctns.sort_values(by="Fecha")
    remisiones = fetch_table_data("remisiones")
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
    if not arribos_expo_ctns.empty:
        # Convert Fecha to datetime if it's not already
        arribos_expo_ctns['Fecha'] = pd.to_datetime(arribos_expo_ctns['Fecha'], errors='coerce')
        arribos_expo_ctns = arribos_expo_ctns.sort_values(by="Fecha")
        arribos_expo_ctns['Fecha'] = arribos_expo_ctns['Fecha'].dt.strftime('%d/%m')
    return arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns

def fetch_last_update():
    update_log = fetch_table_data("update_log")
    if not update_log.empty:
        last_update = update_log[update_log['table_name'] == 'Arribos y existente']['last_update'].max()
        return pd.to_datetime(last_update).strftime("%d/%m/%Y %H:%M")
    return "No disponible"

def assign_to_andresito(table_name, row_data):
    """Assign a travel to Andresito by copying to the andresito table"""
    andresito_table = f"{table_name}_andresito"
    # Add empty columns for Andresito-specific data
    row_data['Chofer'] = ''
    row_data['Patente 1'] = ''
    row_data['Patente 2'] = ''
    if table_name == 'remisiones':
        row_data['Observaciones_Andresito'] = ''
    else:
        row_data['Observaciones'] = ''
    
    insert_data(andresito_table, row_data)

def show_page_trafico2():
    # Load data
    arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns = fetch_data_trafico()
    last_update = fetch_last_update()
    today = datetime.now().strftime('%d/%m') 


    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
        st.info(f'Última actualización: {last_update}')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Operaciones de Tráfico a partir del {current_day}")
    st.markdown("---")
    st.header("IMPO")
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
    st.markdown("---")
    st.header("EXPO")
    col3, col4 = st.columns(2)
    with col3:
        co2_sub, col2_metric1, col2_metric2 = st.columns([6, 1, 1])
        with co2_sub:
            st.subheader("Arribos de Contenedores")
        with col2_metric1:
            st.metric(label="Pendientes hoy", value=arribos_expo_ctns[(arribos_expo_ctns['Estado'] == 'Pendiente') & 
                                                 (arribos_expo_ctns['Fecha'] == today)]['Cantidad'].sum())
        with col2_metric2:
            st.metric(label="Arribados", value=arribos_expo_ctns[(arribos_expo_ctns['Estado'].str.contains('Arribado'))].shape[0])
        st.dataframe(arribos_expo_ctns.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)



    with col4:
        col4_sub, col4_metric, col4_metric2 = st.columns([7, 1, 1])
        with col4_sub:
            st.subheader("Remisiones")
        with col4_metric:
            remisiones_pendientes = 0
            if not remisiones.empty:
                remisiones_pendientes = remisiones[(remisiones['Estado'] == 'Pendiente') & 
                                                     (remisiones['Dia'] == today)].shape[0]
            st.metric(label="Pendientes hoy", value=remisiones_pendientes)
        with col4_metric2:
            remisiones_realizadas = 0
            if not remisiones.empty:
                remisiones_realizadas = remisiones[(remisiones['Estado'].str.contains('Realizado'))].shape[0]
            st.metric(label="Realizadas", value=remisiones_realizadas)
        if not remisiones.empty:
            st.dataframe(remisiones.style.apply(highlight, axis=1), 
                         column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",)} ,
                         hide_index=True, use_container_width=True)
        else:
            st.info("No hay datos de remisiones disponibles")
    st.markdown("---")
    st.header("Asignación a Andresito")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Arribos", "Pendiente Desconsolidar", "Remisiones", "Arribos EXPO CTNs"])
    
    with tab1:
        st.subheader("Asignar Arribos a Andresito")
        if not arribos.empty:
            selected_arribos = st.multiselect(
                "Seleccionar arribos para asignar:",
                options=arribos.index.tolist(),
                format_func=lambda x: f"{arribos.loc[x, 'Contenedor']} - {arribos.loc[x, 'Cliente']}"
            )
            if st.button("Asignar Arribos Seleccionados") and selected_arribos:
                for idx in selected_arribos:
                    row_data = arribos.loc[idx].to_dict()
                    assign_to_andresito('arribos', row_data)
                st.success(f"Se asignaron {len(selected_arribos)} arribos a Andresito")
                st.rerun()
    
    with tab2:
        st.subheader("Asignar Pendiente Desconsolidar a Andresito")
        if not pendiente_desconsolidar.empty:
            selected_pendiente = st.multiselect(
                "Seleccionar pendientes para asignar:",
                options=pendiente_desconsolidar.index.tolist(),
                format_func=lambda x: f"{pendiente_desconsolidar.loc[x, 'Contenedor']} - {pendiente_desconsolidar.loc[x, 'Cliente']}"
            )
            if st.button("Asignar Pendientes Seleccionados") and selected_pendiente:
                for idx in selected_pendiente:
                    row_data = pendiente_desconsolidar.loc[idx].to_dict()
                    assign_to_andresito('pendiente_desconsolidar', row_data)
                st.success(f"Se asignaron {len(selected_pendiente)} pendientes a Andresito")
                st.rerun()
    
    with tab3:
        st.subheader("Asignar Remisiones a Andresito")
        if not remisiones.empty:
            selected_remisiones = st.multiselect(
                "Seleccionar remisiones para asignar:",
                options=remisiones.index.tolist(),
                format_func=lambda x: f"{remisiones.loc[x, 'Contenedor']} - {remisiones.loc[x, 'Cliente']}"
            )
            if st.button("Asignar Remisiones Seleccionadas") and selected_remisiones:
                for idx in selected_remisiones:
                    row_data = remisiones.loc[idx].to_dict()
                    assign_to_andresito('remisiones', row_data)
                st.success(f"Se asignaron {len(selected_remisiones)} remisiones a Andresito")
                st.rerun()
    
    with tab4:
        st.subheader("Asignar Arribos EXPO CTNs a Andresito")
        if not arribos_expo_ctns.empty:
            selected_expo = st.multiselect(
                "Seleccionar arribos EXPO para asignar:",
                options=arribos_expo_ctns.index.tolist(),
                format_func=lambda x: f"{arribos_expo_ctns.loc[x, 'Contenedor']} - {arribos_expo_ctns.loc[x, 'Cliente']}"
            )
            if st.button("Asignar Arribos EXPO Seleccionados") and selected_expo:
                for idx in selected_expo:
                    row_data = arribos_expo_ctns.loc[idx].to_dict()
                    assign_to_andresito('arribos_expo_ctns', row_data)
                st.success(f"Se asignaron {len(selected_expo)} arribos EXPO a Andresito")
                st.rerun()

