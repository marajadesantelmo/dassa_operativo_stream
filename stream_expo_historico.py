import streamlit as st
import pandas as pd
from datetime import datetime

def fetch_data_expo_historico():
    arribos_expo_historico = pd.read_csv('data/arribos_expo_historico.csv')
    historico_retiros_expo = pd.read_csv('data/historico_retiros_expo.csv')
    historico_verificaciones_expo = pd.read_csv('data/historico_verificaciones_expo.csv')
    historico_otros_expo = pd.read_csv('data/historico_otros_expo.csv')
    return arribos_expo_historico, historico_retiros_expo, historico_verificaciones_expo, historico_otros_expo

def show_page_expo_historico():
    arribos_expo_historico, historico_retiros_expo, historico_verificaciones_expo, historico_otros_expo = fetch_data_expo_historico()
    arribos_expo_historico['Fecha'] = pd.to_datetime(arribos_expo_historico['Fecha'])
    historico_retiros_expo['Dia'] = pd.to_datetime(historico_retiros_expo['Dia'])
    historico_verificaciones_expo['Dia'] = pd.to_datetime(historico_verificaciones_expo['Dia'])
    historico_otros_expo['Dia'] = pd.to_datetime(historico_otros_expo['Dia'])
    
    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title("Histórico - Operaciones de expo")

    col1, col2 = st.columns(2)

    with col1: 
        st.subheader("Arribos de contenedores")
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            start_date_arribos = st.date_input("Fecha Inicio", value=arribos_expo_historico['Fecha'].min(), key='start_date_arribos')
            st.write(f"Fecha Inicio: {start_date_arribos.strftime('%d/%m/%Y')}")
        with col1_2:
            end_date_arribos = st.date_input("Fecha Fin", value=arribos_expo_historico['Fecha'].max(), key='end_date_arribos')
            st.write(f"Fecha Fin: {end_date_arribos.strftime('%d/%m/%Y')}")
        
        # Filter data based on selected date range
        filtered_data_arribos = arribos_expo_historico[(arribos_expo_historico['Fecha'] >= pd.to_datetime(start_date_arribos)) & 
                                                       (arribos_expo_historico['Fecha'] <= pd.to_datetime(end_date_arribos))]
        
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
        st.subheader("Retiros")
        col2_1, col2_2, col2_3 = st.columns(3)
        with col2_1:
            start_date_retiros = st.date_input("Fecha Inicio", value=historico_retiros_expo['Dia'].min(), key='start_date_retiros')
            st.write(f"Fecha Inicio: {start_date_retiros.strftime('%d/%m/%Y')}")
        with col2_2:
            end_date_retiros = st.date_input("Fecha Fin", value=historico_retiros_expo['Dia'].max(), key='end_date_retiros')
            st.write(f"Fecha Fin: {end_date_retiros.strftime('%d/%m/%Y')}")
        with col2_3:
            cliente_retiros = st.selectbox("Cliente", options=historico_retiros_expo['Cliente'].unique(), key='cliente_retiros')
            st.write(f"Cliente: {cliente_retiros}")
        
        # Filter data based on selected date range and client
        filtered_data_retiros = historico_retiros_expo.loc[(historico_retiros_expo['Dia'] >= pd.to_datetime(start_date_retiros)) & 
                                                           (historico_retiros_expo['Dia'] <= pd.to_datetime(end_date_retiros)) & 
                                                           (historico_retiros_expo['Cliente'] == cliente_retiros)]
        
        # Format 'Dia' column to show only date part in Spanish format
        filtered_data_retiros['Dia'] = filtered_data_retiros['Dia'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(filtered_data_retiros, hide_index=True, use_container_width=True)

        st.subheader("Otros")
        col2_4, col2_5, col2_6 = st.columns(3)
        with col2_4:
            start_date_otros = st.date_input("Fecha Inicio", value=historico_otros_expo['Dia'].min(), key='start_date_otros')
            st.write(f"Fecha Inicio: {start_date_otros.strftime('%d/%m/%Y')}")
        with col2_5:
            end_date_otros = st.date_input("Fecha Fin", value=historico_otros_expo['Dia'].max(), key='end_date_otros')
            st.write(f"Fecha Fin: {end_date_otros.strftime('%d/%m/%Y')}")
        with col2_6:
            cliente_otros = st.selectbox("Cliente", options=historico_otros_expo['Cliente'].unique(), key='cliente_otros')
            st.write(f"Cliente: {cliente_otros}")
        
        # Filter data based on selected date range and client
        filtered_data_otros = historico_otros_expo.loc[(historico_otros_expo['Dia'] >= pd.to_datetime(start_date_otros)) & 
                                                       (historico_otros_expo['Dia'] <= pd.to_datetime(end_date_otros)) & 
                                                       (historico_otros_expo['Cliente'] == cliente_otros)]
        
        # Format 'Dia' column to show only date part in Spanish format
        filtered_data_otros['Dia'] = filtered_data_otros['Dia'].dt.strftime('%d/%m/%Y')
        
        st.dataframe(filtered_data_otros, hide_index=True, use_container_width=True)


