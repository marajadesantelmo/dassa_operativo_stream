import streamlit as st
import pandas as pd
from datetime import datetime

def fetch_data_impo_historico():
    arribos_impo_historico = pd.read_csv('data/arribos_impo_historico.csv')
    arribos_impo_historico = arribos_impo_historico[arribos_impo_historico['Cliente']=='Grupo Simpa Sa']
    historico_retiros_impo = pd.read_csv('data/historico_retiros_impo.csv')
    historico_retiros_impo = historico_retiros_impo[historico_retiros_impo['Cliente']=='Grupo Simpa Sa']
    historico_verificaciones_impo = pd.read_csv('data/historico_verificaciones_impo.csv')
    historico_verificaciones_impo = historico_verificaciones_impo[historico_verificaciones_impo['Cliente']=='Grupo Simpa Sa']
    historico_otros_impo = pd.read_csv('data/historico_otros_impo.csv')
    historico_otros_impo = historico_otros_impo[historico_otros_impo['Cliente']=='Grupo Simpa Sa']
    return arribos_impo_historico, historico_retiros_impo, historico_verificaciones_impo, historico_otros_impo

def filter_data(data, start_date, end_date, date_column):
    filtered_data = data[(data[date_column] >= pd.to_datetime(start_date)) & 
                         (data[date_column] <= pd.to_datetime(end_date))]
    filtered_data[date_column] = filtered_data[date_column].dt.strftime('%d/%m/%Y')
    return filtered_data

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
            start_date_arribos = st.date_input("Fecha Inicio", value=arribos_impo_historico['Fecha'].min(), key='start_date_arribos')
            st.write(f"Fecha Inicio: {start_date_arribos.strftime('%d/%m/%Y')}")
        with col1_2:
            end_date_arribos = st.date_input("Fecha Fin", value=arribos_impo_historico['Fecha'].max(), key='end_date_arribos')
            st.write(f"Fecha Fin: {end_date_arribos.strftime('%d/%m/%Y')}")
        filtered_data_arribos = filter_data(arribos_impo_historico, start_date_arribos, end_date_arribos, "Fecha")
        
        st.dataframe(filtered_data_arribos, hide_index=True, use_container_width=True)

        st.subheader("Verificaciones")
        col1_4, col1_5, col1_6 = st.columns(3)
        with col1_4:
            start_date_verificaciones = st.date_input("Fecha Inicio", value=historico_verificaciones_impo['Dia'].min(), key='start_date_verificaciones')
            st.write(f"Fecha Inicio: {start_date_verificaciones.strftime('%d/%m/%Y')}")
        with col1_5:
            end_date_verificaciones = st.date_input("Fecha Fin", value=historico_verificaciones_impo['Dia'].max(), key='end_date_verificaciones')
            st.write(f"Fecha Fin: {end_date_verificaciones.strftime('%d/%m/%Y')}")
        filtered_data_verificaciones = filter_data(historico_verificaciones_impo, start_date_verificaciones, end_date_verificaciones, "Dia")        
        st.dataframe(filtered_data_verificaciones, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Retiros")
        col2_1, col2_2, col2_3 = st.columns(3)
        with col2_1:
            start_date_retiros = st.date_input("Fecha Inicio", value=historico_retiros_impo['Dia'].min(), key='start_date_retiros')
            st.write(f"Fecha Inicio: {start_date_retiros.strftime('%d/%m/%Y')}")
        with col2_2:
            end_date_retiros = st.date_input("Fecha Fin", value=historico_retiros_impo['Dia'].max(), key='end_date_retiros')
            st.write(f"Fecha Fin: {end_date_retiros.strftime('%d/%m/%Y')}")
        filtered_data_retiros = filter_data(historico_retiros_impo, start_date_retiros, end_date_retiros, "Dia") 
        st.dataframe(filtered_data_retiros, hide_index=True, use_container_width=True)

        st.subheader("Otros")
        col2_4, col2_5, col2_6 = st.columns(3)
        with col2_4:
            start_date_otros = st.date_input("Fecha Inicio", value=historico_otros_impo['Dia'].min(), key='start_date_otros')
            st.write(f"Fecha Inicio: {start_date_otros.strftime('%d/%m/%Y')}")
        with col2_5:
            end_date_otros = st.date_input("Fecha Fin", value=historico_otros_impo['Dia'].max(), key='end_date_otros')
            st.write(f"Fecha Fin: {end_date_otros.strftime('%d/%m/%Y')}")
        filtered_data_otros = filter_data(historico_otros_impo, start_date_otros, end_date_otros, "Dia")        
        st.dataframe(filtered_data_otros, hide_index=True, use_container_width=True)




