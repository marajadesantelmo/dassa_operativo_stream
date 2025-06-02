import streamlit as st
import pandas as pd
from datetime import datetime

def fetch_data_impo_historico():
    arribos_impo_historico = pd.read_csv('data/arribos_impo_historico.csv')
    arribos_impo_historico['e-tally'] = arribos_impo_historico['e-tally'].fillna("")
    historico_retiros_impo = pd.read_csv('data/historico_retiros_impo.csv')
    historico_retiros_impo['e-tally'] = historico_retiros_impo['e-tally'].fillna("")
    historico_verificaciones_impo = pd.read_csv('data/historico_verificaciones_impo.csv')
    historico_verificaciones_impo['e-tally'] = historico_verificaciones_impo['e-tally'].fillna("")
    return arribos_impo_historico, historico_retiros_impo, historico_verificaciones_impo

def filter_data(data, cliente, start_date, end_date, date_column):
    if cliente == "Todos los clientes":
        filtered_data = data
        st.write("Cliente: todos los clientes")
    else:
        filtered_data = data[data['Cliente'] == cliente]
        st.write(f"Cliente: {cliente}")
    
    filtered_data = filtered_data[(filtered_data[date_column] >= pd.to_datetime(start_date)) & 
                                  (filtered_data[date_column] <= pd.to_datetime(end_date))]
    filtered_data[date_column] = filtered_data[date_column].dt.strftime('%d/%m/%Y')
    return filtered_data

def show_page_impo_historico():
    arribos_impo_historico, historico_retiros_impo, historico_verificaciones_impo = fetch_data_impo_historico()
    arribos_impo_historico['Fecha'] = pd.to_datetime(arribos_impo_historico['Fecha'])
    historico_retiros_impo['Dia'] = pd.to_datetime(historico_retiros_impo['Dia'])
    historico_verificaciones_impo['Dia'] = pd.to_datetime(historico_verificaciones_impo['Dia'])

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
        with col1_3:
            client_options = ["Todos los clientes"] + sorted(list(arribos_impo_historico['Cliente'].unique()))
            cliente_arribos = st.selectbox("Cliente", options=client_options, key='cliente_arribos')
            filtered_data_arribos = filter_data(arribos_impo_historico, cliente_arribos, start_date_arribos, end_date_arribos, "Fecha")
        
        st.dataframe(filtered_data_arribos, 
                    column_config={'e-tally': st.column_config.LinkColumn('e-tally', 
                                                display_text="\U0001F517",)},
                     hide_index=True, use_container_width=True)

        st.subheader("Verificaciones")
        col1_4, col1_5, col1_6 = st.columns(3)
        with col1_4:
            start_date_verificaciones = st.date_input("Fecha Inicio", value=historico_verificaciones_impo['Dia'].min(), key='start_date_verificaciones')
            st.write(f"Fecha Inicio: {start_date_verificaciones.strftime('%d/%m/%Y')}")
        with col1_5:
            end_date_verificaciones = st.date_input("Fecha Fin", value=historico_verificaciones_impo['Dia'].max(), key='end_date_verificaciones')
            st.write(f"Fecha Fin: {end_date_verificaciones.strftime('%d/%m/%Y')}")
        with col1_6:
            client_options = ["Todos los clientes"] + sorted(list(historico_verificaciones_impo['Cliente'].unique()))
            cliente_verificaciones = st.selectbox("Cliente", options=client_options, key='cliente_verificaciones')
            filtered_data_verificaciones = filter_data(historico_verificaciones_impo, cliente_verificaciones, start_date_verificaciones, end_date_verificaciones, "Dia")        
        st.dataframe(filtered_data_verificaciones,                     
                     column_config={'e-tally': st.column_config.LinkColumn('e-tally', 
                                                display_text="\U0001F517",)},
                     hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Retiros")
        col2_1, col2_2, col2_3 = st.columns(3)
        with col2_1:
            start_date_retiros = st.date_input("Fecha Inicio", value=historico_retiros_impo['Dia'].min(), key='start_date_retiros')
            st.write(f"Fecha Inicio: {start_date_retiros.strftime('%d/%m/%Y')}")
        with col2_2:
            end_date_retiros = st.date_input("Fecha Fin", value=historico_retiros_impo['Dia'].max(), key='end_date_retiros')
            st.write(f"Fecha Fin: {end_date_retiros.strftime('%d/%m/%Y')}")
        with col2_3:
            client_options = ["Todos los clientes"] + sorted(list(historico_retiros_impo['Cliente'].unique()))
            cliente_retiros = st.selectbox("Cliente", options=client_options, key='cliente_retiros')
            filtered_data_retiros = filter_data(historico_retiros_impo, cliente_retiros, start_date_retiros, end_date_retiros, "Dia") 
        st.dataframe(filtered_data_retiros,                     
                     column_config={'e-tally': st.column_config.LinkColumn('e-tally', 
                                                display_text="\U0001F517",)},
                     hide_index=True, use_container_width=True)





