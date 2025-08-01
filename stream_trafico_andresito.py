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

    with col2:
        st.subheader("Pendiente Desconsolidar y Vacios")
        st.dataframe(pendiente_desconsolidar, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.header("EXPO")

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Arribos Expo Ctns")
        st.dataframe(arribos_expo_ctns, hide_index=True, use_container_width=True)

    with col4:
        st.subheader("Remisiones")
        st.dataframe(remisiones, column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",)} ,
                    hide_index=True, use_container_width=True)


