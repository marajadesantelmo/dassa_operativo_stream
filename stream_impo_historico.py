import streamlit as st
import pandas as pd

def fetch_data_impo_historico():
    arribos_impo_historico = pd.read_csv('data/arribos_impo_historico.csv')
    return arribos_impo_historico

def show_page_impo_historico():
    arribos_impo_historico = fetch_data_impo_historico()
    
    st.title("Histórico - Operaciones de IMPO")
    st.subheader("Arribos de contenedores")
    
    # Convert 'Fecha' column to datetime
    arribos_impo_historico['Fecha'] = pd.to_datetime(arribos_impo_historico['Fecha'])
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Fecha Inicio", value=arribos_impo_historico['Fecha'].min())
    with col2:
        end_date = st.date_input("Fecha Fin", value=arribos_impo_historico['Fecha'].max())
    
    # Filter data based on selected date range
    filtered_data = arribos_impo_historico[(arribos_impo_historico['Fecha'] >= pd.to_datetime(start_date)) & 
                                           (arribos_impo_historico['Fecha'] <= pd.to_datetime(end_date))]
    
    # Format 'Fecha' column to show only date part in Spanish format
    filtered_data['Fecha'] = filtered_data['Fecha'].dt.strftime('%d/%m/%Y')
    
    st.dataframe(filtered_data, hide_index=True, use_container_width=True)
