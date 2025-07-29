import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight
from supabase_connection import fetch_table_data

@st.cache_data(ttl=60) 
def fetch_data_trafico_andresito():
    arribos = fetch_table_data("arribos_andresito")
    if not arribos.empty:
        arribos = arribos.sort_values(by="Turno")
    
    pendiente_desconsolidar = fetch_table_data("pendiente_desconsolidar_andresito")
    
    arribos_expo_ctns = fetch_table_data("arribos_expo_ctns_andresito")  
    if not arribos_expo_ctns.empty:
        arribos_expo_ctns['Fecha'] = pd.to_datetime(arribos_expo_ctns['Fecha'], format='%d/%m', errors='coerce')
        arribos_expo_ctns = arribos_expo_ctns.sort_values(by="Fecha")
        arribos_expo_ctns['Fecha'] = arribos_expo_ctns['Fecha'].dt.strftime('%d/%m')
    
    remisiones = fetch_table_data("remisiones_andresito")
    if not remisiones.empty:
        remisiones = remisiones[remisiones['Dia'] != '-']
        if not remisiones.empty:
            remisiones['Dia'] = pd.to_datetime(remisiones['Dia'], format='%d/%m', errors='coerce')
            remisiones = remisiones.dropna(subset=['Dia'])
            remisiones.sort_values(by=['Dia'], inplace=True)
            remisiones['Dia'] = remisiones['Dia'].dt.strftime('%d/%m')
            remisiones['Volumen'] = remisiones['Volumen'].round(0).astype(int)
    
    return arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns

def update_andresito_data(table_name, row_index, chofer, patente1, patente2, observaciones):
    """Update Andresito-specific data for a travel"""
    update_data(f"{table_name}_andresito", row_index, {
        'Chofer': chofer,
        'Patente 1': patente1,
        'Patente 2': patente2,
        'Observaciones_Andresito' if table_name == 'remisiones' else 'Observaciones': observaciones
    })

def fetch_last_update():
    update_log = fetch_table_data("update_log")
    if not update_log.empty:
        last_update = update_log[update_log['table_name'] == 'Arribos y existente']['last_update'].max()
        return pd.to_datetime(last_update).strftime("%d/%m/%Y %H:%M")
    return "No disponible"

def show_page_trafico_andresito():
    # Load data
    arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns = fetch_data_trafico_andresito()
    last_update = fetch_last_update()
    today = datetime.now().strftime('%d/%m') 


    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
        st.info(f'Última actualización: {last_update}')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Viajes Asignados a Andresito - {current_day}")
    
    st.markdown("---")
    
    # Edit section
    st.header("📝 Completar Información de Viajes")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Arribos", "Pendiente Desconsolidar", "Remisiones", "Arribos EXPO CTNs"])
    
    with tab1:
        st.subheader("Arribos Asignados")
        if not arribos.empty:
            for idx, row in arribos.iterrows():
                with st.expander(f"📦 {row['Contenedor']} - {row['Cliente']}"):
                    st.write(f"**Booking:** {row['Booking']} | **Estado:** {row['Estado']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        chofer = st.text_input(f"Chofer", value=row.get('Chofer', ''), key=f"chofer_arribos_{idx}")
                        patente1 = st.text_input(f"Patente 1", value=row.get('Patente 1', ''), key=f"patente1_arribos_{idx}")
                    with col2:
                        patente2 = st.text_input(f"Patente 2", value=row.get('Patente 2', ''), key=f"patente2_arribos_{idx}")
                        observaciones = st.text_area(f"Observaciones", value=row.get('Observaciones', ''), key=f"obs_arribos_{idx}")
                    
                    if st.button(f"Actualizar", key=f"update_arribos_{idx}"):
                        update_andresito_data('arribos', idx, chofer, patente1, patente2, observaciones)
                        st.success("Información actualizada")
                        st.rerun()
        else:
            st.info("No hay arribos asignados")
    
    with tab2:
        st.subheader("Pendientes Desconsolidar Asignados")
        if not pendiente_desconsolidar.empty:
            for idx, row in pendiente_desconsolidar.iterrows():
                with st.expander(f"📦 {row['Contenedor']} - {row['Cliente']}"):
                    st.write(f"**Tipo:** {row['Tipo']} | **Estado:** {row['Estado']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        chofer = st.text_input(f"Chofer", value=row.get('Chofer', ''), key=f"chofer_pend_{idx}")
                        patente1 = st.text_input(f"Patente 1", value=row.get('Patente 1', ''), key=f"patente1_pend_{idx}")
                    with col2:
                        patente2 = st.text_input(f"Patente 2", value=row.get('Patente 2', ''), key=f"patente2_pend_{idx}")
                        observaciones = st.text_area(f"Observaciones", value=row.get('Observaciones', ''), key=f"obs_pend_{idx}")
                    
                    if st.button(f"Actualizar", key=f"update_pend_{idx}"):
                        update_andresito_data('pendiente_desconsolidar', idx, chofer, patente1, patente2, observaciones)
                        st.success("Información actualizada")
                        st.rerun()
        else:
            st.info("No hay pendientes asignados")
    
    with tab3:
        st.subheader("Remisiones Asignadas")
        if not remisiones.empty:
            for idx, row in remisiones.iterrows():
                with st.expander(f"📦 {row['Contenedor']} - {row['Cliente']}"):
                    st.write(f"**Booking:** {row['Booking']} | **Estado:** {row['Estado']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        chofer = st.text_input(f"Chofer", value=row.get('Chofer', ''), key=f"chofer_rem_{idx}")
                        patente1 = st.text_input(f"Patente 1", value=row.get('Patente 1', ''), key=f"patente1_rem_{idx}")
                    with col2:
                        patente2 = st.text_input(f"Patente 2", value=row.get('Patente 2', ''), key=f"patente2_rem_{idx}")
                        observaciones = st.text_area(f"Observaciones Andresito", value=row.get('Observaciones_Andresito', ''), key=f"obs_rem_{idx}")
                    
                    if st.button(f"Actualizar", key=f"update_rem_{idx}"):
                        update_andresito_data('remisiones', idx, chofer, patente1, patente2, observaciones)
                        st.success("Información actualizada")
                        st.rerun()
        else:
            st.info("No hay remisiones asignadas")
    
    with tab4:
        st.subheader("Arribos EXPO CTNs Asignados")
        if not arribos_expo_ctns.empty:
            for idx, row in arribos_expo_ctns.iterrows():
                with st.expander(f"📦 {row['Contenedor']} - {row['Cliente']}"):
                    st.write(f"**Booking:** {row['Booking']} | **Estado:** {row['Estado']}")
                    col1, col2 = st.columns(2)
                    with col1:
                        chofer = st.text_input(f"Chofer", value=row.get('Chofer', ''), key=f"chofer_expo_{idx}")
                        patente1 = st.text_input(f"Patente 1", value=row.get('Patente 1', ''), key=f"patente1_expo_{idx}")
                    with col2:
                        patente2 = st.text_input(f"Patente 2", value=row.get('Patente 2', ''), key=f"patente2_expo_{idx}")
                        observaciones = st.text_area(f"Observaciones", value=row.get('Observaciones', ''), key=f"obs_expo_{idx}")
                    
                    if st.button(f"Actualizar", key=f"update_expo_{idx}"):
                        update_andresito_data('arribos_expo_ctns', idx, chofer, patente1, patente2, observaciones)
                        st.success("Información actualizada")
                        st.rerun()
        else:
            st.info("No hay arribos EXPO asignados")

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

