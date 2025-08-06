import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight
from supabase_connection import fetch_table_data, update_data, update_data_by_index

@st.cache_data(ttl=60) 
def fetch_data_trafico_andresito():
    arribos = fetch_table_data("trafico_arribos")
    arribos['Registro'] = pd.to_datetime(arribos['fecha_registro']) - pd.Timedelta(hours=3)
    arribos['Registro'] = arribos['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    arribos = arribos.drop(columns=['fecha_registro','key', 'Tiempo'], errors='ignore')
    
    # Normalize Estado column - treat all "Arribado" statuses as one case
    arribos['Estado_Normalizado'] = arribos['Estado'].apply(
        lambda x: 'Arribado' if pd.notna(x) and 'Arribado' in str(x) else x
    )
    
    pendiente_desconsolidar = fetch_table_data("trafico_pendiente_desconsolidar")
    pendiente_desconsolidar['Registro'] = pd.to_datetime(pendiente_desconsolidar['fecha_registro']) - pd.Timedelta(hours=3)
    pendiente_desconsolidar['Registro'] = pendiente_desconsolidar['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    pendiente_desconsolidar = pendiente_desconsolidar.drop(columns=['Peso', 'Cantidad', 'Envase', 'key', 'fecha_registro'], errors='ignore')
    arribos_expo_ctns = fetch_table_data("trafico_arribos_expo_ctns")   
    arribos_expo_ctns['Registro'] = pd.to_datetime(arribos_expo_ctns['fecha_registro']) - pd.Timedelta(hours=3)
    arribos_expo_ctns['Registro'] = arribos_expo_ctns['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    arribos_expo_ctns = arribos_expo_ctns.drop(columns=['fecha_registro', 'key'], errors='ignore')
    remisiones = fetch_table_data("trafico_remisiones")
    remisiones['Registro'] = pd.to_datetime(remisiones['fecha_registro']) - pd.Timedelta(hours=3)
    remisiones['Registro'] = remisiones['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    remisiones = remisiones.drop(columns=['fecha_registro', 'key'], errors='ignore')

    # Normalize Estado column for remisiones - treat all "Realizado" statuses as one case
    remisiones['Estado_Normalizado'] = remisiones['Estado'].apply(
        lambda x: 'Realizado' if pd.notna(x) and 'Realizado' in str(x) else x
    )

    return arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns


def show_page_trafico_andresito():
    # Load data
    arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns = fetch_data_trafico_andresito()

    st.header("Traslado IMPO")
    col1, col2 = st.columns(2)
    with col1:
        col1a, col1b = st.columns([1, 2])
        with col1a: 
            st.subheader("Traslados desde Puerto a DASSA")
            col1a1, col1b1 = st.columns([2, 1])
            with col1a1:
                estado_options = ["Todos"] + sorted(arribos["Estado_Normalizado"].dropna().unique().tolist())
                selected_estado = st.selectbox("Filtrar por Estado:", estado_options, key="estado_filter_arribos")

                # Apply filter if not "Todos"
                filtered_arribos = arribos
                if selected_estado != "Todos":
                    filtered_arribos = arribos[arribos["Estado_Normalizado"] == selected_estado]
                    
                # Update the arribos variable for the rest of the function
                arribos = filtered_arribos
        with col1b:
            if not arribos.empty:
                st.markdown("**Asignar Chofer - Arribos**")
                col_select1, col_input1, col_button1 = st.columns([2, 2, 1])
                
                with col_select1:
                    selected_arribo_id = st.selectbox(
                        "Seleccionar registro:",
                        options=arribos["id"].unique(),
                        format_func=lambda x: f"ID {x} - {arribos[arribos['id']==x]['Contenedor'].iloc[0] if not arribos[arribos['id']==x].empty else 'N/A'}",
                        key="arribo_select"
                    )
                
                with col_input1:
                    chofer_name_arribos = st.text_input("Chofer:", key="chofer_arribos")
                
                with col_button1:
                    if st.button("Asignar", key="assign_arribos"):
                        if chofer_name_arribos.strip():
                            try:
                                update_data("trafico_arribos", selected_arribo_id, {"chofer": chofer_name_arribos.strip()})
                                st.success(f"Chofer asignado al registro ID {selected_arribo_id}")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al asignar chofer: {e}")
                        else:
                            st.warning("Por favor ingrese el nombre del chofer")
        arribos_display = arribos.copy()
        arribos_display['ID'] = arribos_display['id'].apply(lambda x: f"I{x:03d}")
        cols = ['ID'] + [col for col in arribos_display.columns if col != 'ID']
        arribos_display = arribos_display[cols]
        arribos_display = arribos_display.drop(columns=['id', 'Estado_Normalizado'], errors='ignore')
        st.dataframe(arribos_display.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

    with col2:
        col2a, col2b = st.columns([1, 2])
        with col2a:
            st.subheader("Vacios IMPO a devolver")
            col2a1, col2b1 = st.columns([2, 1])
            with col2a1:
                # Add filter by Estado for pendiente_desconsolidar table
                estado_options_pendiente = ["Todos"] + sorted(pendiente_desconsolidar["Estado"].dropna().unique().tolist())
                selected_estado_pendiente = st.selectbox("Filtrar por Estado:", estado_options_pendiente, key="estado_filter_pendiente")

                # Apply filter if not "Todos"
                filtered_pendiente_desconsolidar = pendiente_desconsolidar
                if selected_estado_pendiente != "Todos":
                    filtered_pendiente_desconsolidar = pendiente_desconsolidar[pendiente_desconsolidar["Estado"] == selected_estado_pendiente]
                    
                # Update the pendiente_desconsolidar variable for the rest of the function
                pendiente_desconsolidar = filtered_pendiente_desconsolidar
        with col2b:
            if not pendiente_desconsolidar.empty:
                st.markdown("**Asignar Chofer - Pendiente Desconsolidar**")
                col_select2, col_input2, col_button2 = st.columns([2, 2, 1])
                
                with col_select2:
                    selected_pendiente_id = st.selectbox(
                        "Seleccionar registro:",
                        options=pendiente_desconsolidar["id"].unique(),
                        format_func=lambda x: f"ID {x} - {pendiente_desconsolidar[pendiente_desconsolidar['id']==x]['Contenedor'].iloc[0] if not pendiente_desconsolidar[pendiente_desconsolidar['id']==x].empty else 'N/A'}",
                        key="pendiente_select"
                    )
                
                with col_input2:
                    chofer_name_pendiente = st.text_input("Chofer:", key="chofer_pendiente")
                
                with col_button2:
                    if st.button("Asignar", key="assign_pendiente"):
                        if chofer_name_pendiente.strip():
                            try:
                                update_data("trafico_pendiente_desconsolidar", selected_pendiente_id, {"chofer": chofer_name_pendiente.strip()})
                                st.success(f"Chofer asignado al registro ID {selected_pendiente_id}")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al asignar chofer: {e}")
                        else:
                            st.warning("Por favor ingrese el nombre del chofer")
        pendiente_desconsolidar_display = pendiente_desconsolidar.copy()
        pendiente_desconsolidar_display['ID'] = pendiente_desconsolidar_display['id'].apply(lambda x: f"V{x:03d}")
        cols = ['ID'] + [col for col in pendiente_desconsolidar_display.columns if col != 'ID']
        pendiente_desconsolidar_display = pendiente_desconsolidar_display[cols]
        pendiente_desconsolidar_display = pendiente_desconsolidar_display.drop(columns=['id'], errors='ignore')
        st.dataframe(pendiente_desconsolidar_display.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)
        
    st.markdown("---")
    st.header("Traslado EXPO")

    col3, col4 = st.columns(2)
    with col3:
        col3a, col3b = st.columns([1, 2])
        with col3a:
            st.subheader("Retiros de Vacíos EXPO")
            col3a1, col3b1 = st.columns([2, 1])
            with col3a1:
                # Add filter by Estado for arribos_expo_ctns table
                estado_options_expo = ["Todos"] + sorted(arribos_expo_ctns["Estado"].dropna().unique().tolist())
                selected_estado_expo = st.selectbox("Filtrar por Estado:", estado_options_expo, key="estado_filter_expo")

                # Apply filter if not "Todos"
                filtered_arribos_expo_ctns = arribos_expo_ctns
                if selected_estado_expo != "Todos":
                    filtered_arribos_expo_ctns = arribos_expo_ctns[arribos_expo_ctns["Estado"] == selected_estado_expo]
                    
                # Update the arribos_expo_ctns variable for the rest of the function
                arribos_expo_ctns = filtered_arribos_expo_ctns
        with col3b:
            # Add chofer assignment for arribos_expo_ctns
            if not arribos_expo_ctns.empty:
                st.markdown("**Asignar Chofer - Arribos Expo Ctns**")
                col_select3, col_input3, col_button3 = st.columns([2, 2, 1])
                
                with col_select3:
                    selected_expo_id = st.selectbox(
                        "Seleccionar registro:",
                        options=arribos_expo_ctns["id"].unique(),
                        format_func=lambda x: f"ID {x} - {arribos_expo_ctns[arribos_expo_ctns['id']==x]['Booking'].iloc[0] if not arribos_expo_ctns[arribos_expo_ctns['id']==x].empty else 'N/A'}",
                        key="expo_select"
                    )
                
                with col_input3:
                    chofer_name_expo = st.text_input("Chofer:", key="chofer_expo")
                
                with col_button3:
                    if st.button("Asignar", key="assign_expo"):
                        if chofer_name_expo.strip():
                            try:
                                update_data("trafico_arribos_expo_ctns", selected_expo_id, {"chofer": chofer_name_expo.strip()})
                                st.success(f"Chofer asignado al registro ID {selected_expo_id}")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al asignar chofer: {e}")
                        else:
                            st.warning("Por favor ingrese el nombre del chofer")
        arribos_expo_ctns_display = arribos_expo_ctns.copy()
        arribos_expo_ctns_display['ID'] = arribos_expo_ctns_display['id'].apply(lambda x: f"E{x:03d}")
        cols = ['ID'] + [col for col in arribos_expo_ctns_display.columns if col != 'ID']
        arribos_expo_ctns_display = arribos_expo_ctns_display[cols]
        arribos_expo_ctns_display = arribos_expo_ctns_display.drop(columns=['id'], errors='ignore')
        arribos_expo_ctns_display['Estado'] = arribos_expo_ctns_display['Estado'].fillna('Pendiente')
        st.dataframe(arribos_expo_ctns_display.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

    with col4:
        col4a, col4b = st.columns([1, 2])
        with col4a:
            st.subheader("Remisiones de DASSA a puerto")
            col4a1, col4b1 = st.columns([2, 1])
            with col4a1:
                # Add filter by Estado for remisiones table using normalized Estado
                estado_options_remisiones = ["Todos"] + sorted(remisiones["Estado_Normalizado"].dropna().unique().tolist())
                selected_estado_remisiones = st.selectbox("Filtrar por Estado:", estado_options_remisiones, key="estado_filter_remisiones")

                # Apply filter if not "Todos"
                filtered_remisiones = remisiones
                if selected_estado_remisiones != "Todos":
                    filtered_remisiones = remisiones[remisiones["Estado_Normalizado"] == selected_estado_remisiones]
                    
                # Update the remisiones variable for the rest of the function
                remisiones = filtered_remisiones
        with col4b:
            # Add chofer assignment for remisiones
            if not remisiones.empty:
                st.markdown("**Asignar Chofer - Remisiones**")
                col_select4, col_input4, col_button4 = st.columns([2, 2, 1])
                
                with col_select4:
                    selected_remision_id = st.selectbox(
                        "Seleccionar registro:",
                        options=remisiones["id"].unique(),
                        format_func=lambda x: f"ID {x} - {remisiones[remisiones['id']==x]['Booking'].iloc[0] if not remisiones[remisiones['id']==x].empty else 'N/A'}",
                        key="remision_select"
                    )
                
                with col_input4:
                    chofer_name_remisiones = st.text_input("Chofer:", key="chofer_remisiones")
                
                with col_button4:
                    if st.button("Asignar", key="assign_remisiones"):
                        if chofer_name_remisiones.strip():
                            try:
                                update_data("trafico_remisiones", selected_remision_id, {"chofer": chofer_name_remisiones.strip()})
                                st.success(f"Chofer asignado al registro ID {selected_remision_id}")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al asignar chofer: {e}")
                        else:
                            st.warning("Por favor ingrese el nombre del chofer")
        remisiones_display = remisiones.copy()
        remisiones_display['ID'] = remisiones_display['id'].apply(lambda x: f"B{x:03d}")
        cols = ['ID'] + [col for col in remisiones_display.columns if col != 'ID']
        remisiones_display = remisiones_display[cols]
        remisiones_display = remisiones_display.drop(columns=['id', 'Estado_Normalizado'], errors='ignore')
        st.dataframe(remisiones_display.style.apply(highlight, axis=1), column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",)}, 
                     hide_index=True, use_container_width=True)



