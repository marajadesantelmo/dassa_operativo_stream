import streamlit as st
import pandas as pd
from datetime import datetime

def fetch_data_expo_historico():
    arribos_expo_carga_historico = pd.read_csv('data/arribos_expo_carga_historico.csv')
    arribos_expo_ctns_historico = pd.read_csv('data/arribos_expo_ctns_historico.csv')
    historico_verificaciones_expo = pd.read_csv('data/historico_verificaciones_expo.csv')
    historico_otros_expo = pd.read_csv('data/historico_otros_expo.csv')
    historico_remisiones = pd.read_csv('data/historico_remisiones.csv')
    historico_consolidados = pd.read_csv('data/historico_consolidados.csv') # Hay que armar algo con el egresado
    return arribos_expo_carga_historico, arribos_expo_ctns_historico, historico_verificaciones_expo, historico_otros_expo, historico_remisiones, historico_consolidados

def show_page_expo_historico():
    arribos_expo_carga_historico, arribos_expo_ctns_historico, historico_verificaciones_expo, historico_otros_expo, historico_remisiones, historico_consolidados = fetch_data_expo_historico()
    arribos_expo_carga_historico['Fecha'] = pd.to_datetime(arribos_expo_carga_historico['Fecha'])
    arribos_expo_ctns_historico['Fecha'] = pd.to_datetime(arribos_expo_ctns_historico['Fecha'])
    historico_verificaciones_expo['Dia'] = pd.to_datetime(historico_verificaciones_expo['Dia'])
    historico_otros_expo['Dia'] = pd.to_datetime(historico_otros_expo['Dia'])
    historico_remisiones['Dia'] = pd.to_datetime(historico_remisiones['Dia'])
    historico_consolidados['Dia'] = pd.to_datetime(historico_consolidados['Dia'])
    
    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title("Histórico - Operaciones de Expo")

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
            cliente_arribos_carga = st.selectbox("Cliente", options=arribos_expo_carga_historico['Cliente'].unique(), key='cliente_arribos_carga')
            st.write(f"Cliente: {cliente_arribos_carga}")
        
        # Filter data based on selected date range
        filtered_data_arribos = arribos_expo_carga_historico[(arribos_expo_carga_historico['Fecha'] >= pd.to_datetime(start_date_arribos_carga)) & 
                                                       (arribos_expo_carga_historico['Fecha'] <= pd.to_datetime(end_date_arribos_cargas)) &
                                                         (arribos_expo_carga_historico['Cliente'] == cliente_arribos_carga)]
        
        # Format 'Fecha' column to show only date part in Spanish format
        filtered_data_arribos['Fecha'] = filtered_data_arribos['Fecha'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(filtered_data_arribos, hide_index=True, use_container_width=True)

        st.subheader("Verificaciones")
        col1_4, col1_5, col1_6 = st.columns(3)
        with col1_4:
            start_date_verificaciones = st.date_input("Fecha Inicio", value=historico_verificaciones_expo['Dia'].min(), key='start_date_verificaciones')
            st.write(f"Fecha Inicio: {start_date_verificaciones.strftime('%d/%m/%Y')}")
        with col1_5:
            end_date_verificaciones = st.date_input("Fecha Fin", value=historico_verificaciones_expo['Dia'].max(), key='end_date_verificaciones')
            st.write(f"Fecha Fin: {end_date_verificaciones.strftime('%d/%m/%Y')}")
        with col1_6:
            cliente_verificaciones = st.selectbox("Cliente", options=historico_verificaciones_expo['Cliente'].unique(), key='cliente_verificaciones')
            st.write(f"Cliente: {cliente_verificaciones}")
        
        # Filter data based on selected date range and client
        filtered_data_verificaciones = historico_verificaciones_expo.loc[(historico_verificaciones_expo['Dia'] >= pd.to_datetime(start_date_verificaciones)) & 
                                                                         (historico_verificaciones_expo['Dia'] <= pd.to_datetime(end_date_verificaciones)) & 
                                                                         (historico_verificaciones_expo['Cliente'] == cliente_verificaciones)]
        
        # Format 'Dia' column to show only date part in Spanish format
        filtered_data_verificaciones['Dia'] = filtered_data_verificaciones['Dia'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(filtered_data_verificaciones, hide_index=True, use_container_width=True)

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
            cliente_arribos_ctns = st.selectbox("Cliente", options=arribos_expo_ctns_historico['Cliente'].unique(), key='cliente_arribos_ctns')
            st.write(f"Cliente: {cliente_arribos_ctns}")
        
        filtered_data_arribos_ctns = arribos_expo_ctns_historico.loc[(arribos_expo_ctns_historico['Fecha'] >= pd.to_datetime(start_date_arribos_ctns)) &
                                                                    (arribos_expo_ctns_historico['Fecha'] <= pd.to_datetime(end_date_arribos_ctns)) &
                                                                    (arribos_expo_ctns_historico['Cliente'] == cliente_arribos_ctns)]
        filtered_data_arribos_ctns['Fecha'] = filtered_data_arribos_ctns['Fecha'].dt.strftime('%d/%m/%Y')
        st.dataframe(filtered_data_arribos_ctns, hide_index=True, use_container_width=True)

        st.subheader("Remisiones")
        col2_4, col2_5, col2_6 = st.columns(3)
        with col2_4:
            start_date_remisiones = st.date_input("Fecha Inicio", value=historico_remisiones['Dia'].min(), key='start_date_remisiones')
            st.write(f"Fecha Inicio: {start_date_remisiones.strftime('%d/%m/%Y')}")
        with col2_5:
            end_date_remisiones = st.date_input("Fecha Fin", value=historico_remisiones['Dia'].max(), key='end_date_remisiones')
            st.write(f"Fecha Fin: {end_date_remisiones.strftime('%d/%m/%Y')}")
        with col2_6:
            cliente_remisiones = st.selectbox("Cliente", options=historico_remisiones['Cliente'].unique(), key='cliente_remisiones')
            st.write(f"Cliente: {cliente_remisiones}")
        
        # Filter data based on selected date range and client
        filtered_data_remisiones = historico_remisiones.loc[(historico_remisiones['Dia'] >= pd.to_datetime(start_date_remisiones)) & 
                                                       (historico_remisiones['Dia'] <= pd.to_datetime(end_date_remisiones)) & 
                                                       (historico_remisiones['Cliente'] == cliente_remisiones)]
        
        # Format 'Dia' column to show only date part in Spanish format
        filtered_data_remisiones['Dia'] = filtered_data_remisiones['Dia'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(filtered_data_remisiones, hide_index=True, use_container_width=True)
    