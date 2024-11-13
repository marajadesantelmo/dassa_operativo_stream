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
    start_date = st.date_input("Start date", value=arribos_impo_historico['Fecha'].min())
    end_date = st.date_input("End date", value=arribos_impo_historico['Fecha'].max())
    
    # Filter data based on selected date range
    filtered_data = arribos_impo_historico[(arribos_impo_historico['Fecha'] >= pd.to_datetime(start_date)) & 
                                           (arribos_impo_historico['Fecha'] <= pd.to_datetime(end_date))]
    
    st.dataframe(filtered_data, hide_index=True, use_container_width=True)
