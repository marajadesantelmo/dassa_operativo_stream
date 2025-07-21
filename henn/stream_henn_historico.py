import streamlit as st
import pandas as pd
from datetime import datetime
import time

def fetch_data_historico():
    arribos_expo_carga_historico = pd.read_csv('data/arribos_expo_carga_historico.csv')
    arribos_expo_carga_historico = arribos_expo_carga_historico[arribos_expo_carga_historico['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    arribos_expo_ctns_historico = pd.read_csv('data/arribos_expo_ctns_historico.csv')
    arribos_expo_ctns_historico = arribos_expo_ctns_historico[arribos_expo_ctns_historico['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    historico_verificaciones_expo = pd.read_csv('data/historico_verificaciones_expo.csv')
    historico_verificaciones_expo = historico_verificaciones_expo[historico_verificaciones_expo['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    historico_otros_expo = pd.read_csv('data/historico_otros_expo.csv')
    historico_otros_expo = historico_otros_expo[historico_otros_expo['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    return arribos_expo_carga_historico, arribos_expo_ctns_historico, historico_verificaciones_expo

def filter_data(data, start_date, end_date, date_column):
    filtered_data = data[(data[date_column] >= pd.to_datetime(start_date)) & 
                         (data[date_column] <= pd.to_datetime(end_date))]
    filtered_data[date_column] = filtered_data[date_column].dt.strftime('%d/%m/%Y')
    return filtered_data

def show_page_historico():
    arribos_expo_carga_historico, arribos_expo_ctns_historico,  historico_verificaciones_expo = fetch_data_historico()
    
    # Convert date columns to datetime
    date_columns = {
        'arribos_expo_carga_historico': 'Fecha',
        'arribos_expo_ctns_historico': 'Fecha',
        'historico_verificaciones_expo': 'Dia' }
    for df_name, date_col in date_columns.items():
        df = locals()[df_name]
        if not df.empty:
            df[date_col] = pd.to_datetime(df[date_col])
    
    
    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        st.header("Histórico - Operaciones de Expo")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_henn.png')
    col1, col2 = st.columns(2)

    col1, col2 = st.columns(2)

    with col1: 
        st.subheader("Arribos de carga")
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            start_date_arribos_carga = st.date_input("Fecha Inicio", value=arribos_expo_carga_historico['Fecha'].min(), key='start_date_arribos_carga')
            st.write(f"Fecha Inicio: {start_date_arribos_carga.strftime('%d/%m/%Y')}")
        with col1_2:
            end_date_arribos_cargas = st.date_input("Fecha Fin", value=arribos_expo_carga_historico['Fecha'].max(), key='end_date_arribos_cargas')
            st.write(f"Fecha Fin: {end_date_arribos_cargas.strftime('%d/%m/%Y')}")
        with col1_3:
            client_options = ["Todos los clientes"] + sorted(list(arribos_expo_carga_historico['Cliente'].unique()))
            cliente_arribos_carga = st.selectbox("Cliente", options=client_options, key='cliente_arribos_carga')
            filtered_data_arribos = filter_data(arribos_expo_carga_historico, start_date_arribos_carga, end_date_arribos_cargas, "Fecha")
        
        st.dataframe(filtered_data_arribos, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Arribos de Contenedores")
        col2_1, col2_2, col2_3 = st.columns(3)
        with col2_1:
            start_date_arribos_ctns = st.date_input("Fecha Inicio", value=arribos_expo_ctns_historico['Fecha'].min(), key='start_date_arribos_ctns')
            st.write(f"Fecha Inicio: {start_date_arribos_ctns.strftime('%d/%m/%Y')}")
        with col2_2:
            end_date_arribos_ctns = st.date_input("Fecha Fin", value=arribos_expo_ctns_historico['Fecha'].max(), key='end_date_arribos_ctns')
            st.write(f"Fecha Fin: {end_date_arribos_ctns.strftime('%d/%m/%Y')}")
        with col2_3:
            filtered_data_arribos_ctns = filter_data(arribos_expo_ctns_historico, start_date_arribos_ctns, end_date_arribos_ctns, "Fecha")
        st.dataframe(filtered_data_arribos_ctns, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    while True:
        show_page_historico
        time.sleep(60)  
        st.experimental_rerun()

