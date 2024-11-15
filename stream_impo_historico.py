import streamlit as st
import pandas as pd
from datetime import datetime

def fetch_data_impo_historico():
    arribos_impo_historico = pd.read_csv('data/arribos_impo_historico.csv')
    historico_retiros_impo = pd.read_csv('data/historico_retiros_impo.csv')
    historico_verificaciones_impo = pd.read_csv('data/historico_verificaciones_impo.csv')
    historico_otros_impo = pd.read_csv('data/historico_otros_impo.csv')
    return arribos_impo_historico, historico_retiros_impo, historico_verificaciones_impo, historico_otros_impo

def show_page_impo_historico():
    arribos_impo_historico, historico_retiros_impo, historico_verificaciones_impo, historico_otros_impo = fetch_data_impo_historico()
    arribos_impo_historico['Fecha'] = pd.to_datetime(arribos_impo_historico['Fecha'])
    historico_retiros_impo['Dia'] = pd.to_datetime(historico_retiros_impo['Dia'])
    historico_verificaciones_impo['Dia'] = pd.to_datetime(historico_verificaciones_impo['Dia'])
    historico_otros_impo['Dia'] = pd.to_datetime(historico_otros_impo['Dia'])
    
    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title("Histórico - Operaciones de IMPO")

    col1, col2 = st.columns(2)

    with col1: 
        st.subheader("Arribos de contenedores")
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            start_date = st.date_input("Fecha Inicio", value=arribos_impo_historico['Fecha'].min(), label_visibility="collapsed")
            st.write(f"Fecha Inicio: {start_date.strftime('%d/%m/%Y')}")
        with col1_2:
            end_date = st.date_input("Fecha Fin", value=arribos_impo_historico['Fecha'].max(), label_visibility="collapsed")
            st.write(f"Fecha Fin: {end_date.strftime('%d/%m/%Y')}")
        with col1_3:
            cliente = st.selectbox("Cliente", options=arribos_impo_historico['Cliente'].unique(), label_visibility="collapsed")
            st.write(f"Cliente: {cliente}")
        # Filter data based on selected date range
        arribos_impo_historico_filtrado = arribos_impo_historico.loc[(arribos_impo_historico['Fecha'] >= pd.to_datetime(start_date)) & 
                                            (arribos_impo_historico['Fecha'] <= pd.to_datetime(end_date)) &
                                            (arribos_impo_historico['Cliente'] == cliente),]
        # Format 'Fecha' column to show only date part in Spanish format
        arribos_impo_historico_filtrado['Fecha'] = arribos_impo_historico_filtrado['Fecha'].dt.strftime('%d/%m/%Y')
        st.dataframe(arribos_impo_historico_filtrado, hide_index=True, use_container_width=True)

        st.subheader("Verificaciones")
        col1_4, col1_5, col1_6 = st.columns(3)
        with col1_4:
            start_date = st.date_input("Fecha Inicio", value=historico_verificaciones_impo['Dia'].min(), label_visibility="collapsed")
            st.write(f"Fecha Inicio: {start_date.strftime('%d/%m/%Y')}")
        with col1_5:
            end_date = st.date_input("Fecha Fin", value=historico_verificaciones_impo['Dia'].max(), label_visibility="collapsed")
            st.write(f"Fecha Fin: {end_date.strftime('%d/%m/%Y')}")
        with col1_6:
            cliente = st.selectbox("Cliente", options=historico_verificaciones_impo['Cliente'].unique(), label_visibility="collapsed")
            st.write(f"Cliente: {cliente}")
        # Filter data based on selected date range
        historico_verificaciones_impo = historico_verificaciones_impo.loc[(historico_verificaciones_impo['Dia'] >= pd.to_datetime(start_date)) &
                                            (historico_verificaciones_impo['Dia'] <= pd.to_datetime(end_date)) &
                                            (arribos_impo_historico['Cliente'] == cliente),]
        # Format 'Dia' column to show only date part in Spanish format
        historico_verificaciones_impo['Dia'] = historico_verificaciones_impo['Dia'].dt.strftime('%d/%m/%Y')
        st.dataframe(historico_verificaciones_impo, hide_index=True, use_container_width=True)
        

    with col2:
        st.subheader("Retiros")
        col2_1, col2_2, col2_3 = st.columns(3)
        with col2_1:
            start_date = st.date_input("Fecha Inicio", value=historico_retiros_impo['Dia'].min(), label_visibility="collapsed")
            st.write(f"Fecha Inicio: {start_date.strftime('%d/%m/%Y')}")
        with col2_2:
            end_date = st.date_input("Fecha Fin", value=historico_retiros_impo['Dia'].max(), label_visibility="collapsed")
            st.write(f"Fecha Fin: {end_date.strftime('%d/%m/%Y')}")
        with col2_3:
            cliente = st.selectbox("Cliente", options=historico_retiros_impo['Cliente'].unique(), label_visibility="collapsed")
            st.write(f"Cliente: {cliente}")
        # Filter data based on selected date range
        historico_retiros_impo = historico_retiros_impo.loc[(historico_retiros_impo['Dia'] >= pd.to_datetime(start_date)) & 
                                            (historico_retiros_impo['Dia'] <= pd.to_datetime(end_date)) &
                                            (arribos_impo_historico['Cliente'] == cliente),]
        # Format 'Dia' column to show only date part in Spanish format
        historico_retiros_impo['Dia'] = historico_retiros_impo['Dia'].dt.strftime('%d/%m/%Y')
        st.dataframe(historico_retiros_impo, hide_index=True, use_container_width=True)

        st.subheader("Otros")
        col2_4, col2_5, col2_6 = st.columns(3)
        with col2_4:
            start_date = st.date_input("Fecha Inicio", value=historico_otros_impo['Dia'].min(), label_visibility="collapsed")
            st.write(f"Fecha Inicio: {start_date.strftime('%d/%m/%Y')}")
        with col2_5:
            end_date = st.date_input("Fecha Fin", value=historico_otros_impo['Dia'].max(), label_visibility="collapsed")
            st.write(f"Fecha Fin: {end_date.strftime('%d/%m/%Y')}")
        with col2_6:
            cliente = st.selectbox("Cliente", options=historico_otros_impo['Cliente'].unique(), label_visibility="collapsed")
            st.write(f"Cliente: {cliente}")
        # Filter data based on selected date range
        historico_otros_impo = historico_otros_impo.loc[(historico_otros_impo['Dia'] >= pd.to_datetime(start_date)) & 
                                            (historico_otros_impo['Dia'] <= pd.to_datetime(end_date)) &
                                            (arribos_impo_historico['Cliente'] == cliente),]
        # Format 'Dia' column to show only date part in Spanish format
        historico_otros_impo['Dia'] = historico_otros_impo['Dia'].dt.strftime('%d/%m/%Y')
        st.dataframe(historico_otros_impo, hide_index=True, use_container_width=True)




