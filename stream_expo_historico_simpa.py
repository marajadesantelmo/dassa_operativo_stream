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
            client_options = ["Todos los clientes"] + sorted(list(arribos_expo_carga_historico['Cliente'].unique()))
            cliente_arribos_carga = st.selectbox("Cliente", options=client_options, key='cliente_arribos_carga')
            filtered_data_arribos = filter_data(arribos_expo_carga_historico, cliente_arribos_carga, start_date_arribos_carga, end_date_arribos_cargas, "Fecha")
        
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
            client_options = ["Todos los clientes"] + sorted(list(arribos_expo_carga_historico['Cliente'].unique()))
            cliente_verificaciones = st.selectbox("Cliente", options=client_options, key='cliente_verificaciones')
            filtered_data_verificaciones = filter_data(historico_verificaciones_expo, cliente_verificaciones, start_date_verificaciones, end_date_verificaciones, "Dia")
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
            client_options = ["Todos los clientes"] + sorted(list(arribos_expo_carga_historico['Cliente'].unique()))
            cliente_arribos_ctns = st.selectbox("Cliente", options=client_options, key='cliente_arribos_ctns')
            filtered_data_arribos_ctns = filter_data(arribos_expo_ctns_historico, cliente_arribos_ctns, start_date_arribos_ctns, end_date_arribos_ctns, "Fecha")
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
            client_options = ["Todos los clientes"] + sorted(list(arribos_expo_carga_historico['Cliente'].unique()))
            cliente_remisiones = st.selectbox("Cliente", options=client_options, key='cliente_remisiones')
            filtered_data_remisiones = filter_data(historico_remisiones, cliente_remisiones, start_date_remisiones, end_date_remisiones, "Dia")
        st.dataframe(filtered_data_remisiones, hide_index=True, use_container_width=True)
