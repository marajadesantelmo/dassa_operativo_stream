import streamlit as st
import pandas as pd
from datetime import datetime

def fetch_data_impo_historico():
    arribos_impo_historico = pd.read_csv('data/arribos_impo_historico.csv')
    historico_retiros_impo = pd.read_csv('data/historico_retiros_impo.csv')
    return arribos_impo_historico, historico_retiros_impo

def show_page_impo_historico():
    arribos_impo_historico, historico_retiros_impo = fetch_data_impo_historico()
    arribos_impo_historico['Fecha'] = pd.to_datetime(arribos_impo_historico['Fecha'])
    historico_retiros_impo['Dia'] = pd.to_datetime(historico_retiros_impo['Dia'])
    
    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title("Histórico - Operaciones de IMPO")

    col1, col2 = st.columns(2)

    with col1: 
        st.subheader("Arribos de contenedores")
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            start_date = st.date_input("Fecha Inicio", value=arribos_impo_historico['Fecha'].min(), label_visibility="collapsed")
            st.write(f"Fecha Inicio: {start_date.strftime('%d/%m/%Y')}")
        with col1_2:
            end_date = st.date_input("Fecha Fin", value=arribos_impo_historico['Fecha'].max(), label_visibility="collapsed")
            st.write(f"Fecha Fin: {end_date.strftime('%d/%m/%Y')}")
        # Filter data based on selected date range
        filtered_data = arribos_impo_historico[(arribos_impo_historico['Fecha'] >= pd.to_datetime(start_date)) & 
                                            (arribos_impo_historico['Fecha'] <= pd.to_datetime(end_date))]
        # Format 'Fecha' column to show only date part in Spanish format
        filtered_data['Fecha'] = filtered_data['Fecha'].dt.strftime('%d/%m/%Y')
        st.dataframe(filtered_data, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Retiros")
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            start_date = st.date_input("Fecha Inicio", value=historico_retiros_impo['Dia'].min(), label_visibility="collapsed")
            st.write(f"Fecha Inicio: {start_date.strftime('%d/%m/%Y')}")
        with col2_2:
            end_date = st.date_input("Fecha Fin", value=historico_retiros_impo['Dia'].max(), label_visibility="collapsed")
            st.write(f"Fecha Fin: {end_date.strftime('%d/%m/%Y')}")
        # Filter data based on selected date range
        filtered_data = historico_retiros_impo[(historico_retiros_impo['Dia'] >= pd.to_datetime(start_date)) & 
                                            (historico_retiros_impo['Dia'] <= pd.to_datetime(end_date))]
        # Format 'Dia' column to show only date part in Spanish format
        filtered_data['Dia'] = filtered_data['Dia'].dt.strftime('%d/%m/%Y')
        st.dataframe(filtered_data, hide_index=True, use_container_width=True)

