import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight
from supabase_connection import fetch_table_data, update_data, update_data_by_index

@st.cache_data(ttl=60) 
def fetch_data_trafico_andresito():
    arribos = fetch_table_data("trafico_arribos")  
    pendiente_desconsolidar = fetch_table_data("trafico_pendiente_desconsolidar")
    arribos_expo_ctns = fetch_table_data("trafico_arribos_expo_ctns")   
    remisiones = fetch_table_data("trafico_remisiones")
    return arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns


def show_page_trafico_andresito():
    # Load data
    arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns = fetch_data_trafico_andresito()

    st.header("IMPO")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Arribos")
        st.dataframe(arribos, hide_index=True, use_container_width=True)
        
        # Asignar Chofer - Arribos
        if not arribos.empty:
            st.markdown("**Asignar Chofer:**")
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

    with col2:
        st.subheader("Pendiente Desconsolidar y Vacios")
        st.dataframe(pendiente_desconsolidar, hide_index=True, use_container_width=True)
        
        # Asignar Chofer - Pendiente Desconsolidar
        if not pendiente_desconsolidar.empty:
            st.markdown("**Asignar Chofer:**")
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

    st.markdown("---")
    st.header("EXPO")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Arribos Expo Ctns")
        st.dataframe(arribos_expo_ctns, hide_index=True, use_container_width=True)
        
        # Asignar Chofer - Arribos Expo Ctns
        if not arribos_expo_ctns.empty:
            st.markdown("**Asignar Chofer:**")
            col_select3, col_input3, col_button3 = st.columns([2, 2, 1])
            
            with col_select3:
                selected_expo_id = st.selectbox(
                    "Seleccionar registro:",
                    options=arribos_expo_ctns["id"].unique(),
                    format_func=lambda x: f"ID {x} - {arribos_expo_ctns[arribos_expo_ctns['id']==x]['Contenedor'].iloc[0] if not arribos_expo_ctns[arribos_expo_ctns['id']==x].empty else 'N/A'}",
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

    with col4:
        st.subheader("Remisiones")
        st.dataframe(remisiones, column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",)} ,
                    hide_index=True, use_container_width=True)
        
        # Asignar Chofer - Remisiones
        if not remisiones.empty:
            st.markdown("**Asignar Chofer:**")
            col_select4, col_input4, col_button4 = st.columns([2, 2, 1])
            
            with col_select4:
                selected_remision_id = st.selectbox(
                    "Seleccionar registro:",
                    options=remisiones["id"].unique(),
                    format_func=lambda x: f"ID {x} - {remisiones[remisiones['id']==x]['Contenedor'].iloc[0] if not remisiones[remisiones['id']==x].empty else 'N/A'}",
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


