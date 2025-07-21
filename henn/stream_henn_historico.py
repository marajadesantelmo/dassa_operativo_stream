import streamlit as st
import pandas as pd
from datetime import datetime
import time

def fetch_data_impo_historico():
    arribos_impo_historico = pd.read_csv('data/arribos_impo_historico.csv')
    arribos_impo_historico = arribos_impo_historico[arribos_impo_historico['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    historico_retiros_impo = pd.read_csv('data/historico_retiros_impo.csv')
    historico_retiros_impo = historico_retiros_impo[historico_retiros_impo['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    historico_verificaciones_impo = pd.read_csv('data/historico_verificaciones_impo.csv')
    historico_verificaciones_impo = historico_verificaciones_impo[historico_verificaciones_impo['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    historico_otros_impo = pd.read_csv('data/historico_otros_impo.csv')
    historico_otros_impo = historico_otros_impo[historico_otros_impo['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    arribos_expo_carga_historico = pd.read_csv('data/arribos_expo_carga_historico.csv')
    arribos_expo_carga_historico = arribos_expo_carga_historico[arribos_expo_carga_historico['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    arribos_expo_ctns_historico = pd.read_csv('data/arribos_expo_ctns_historico.csv')
    arribos_expo_ctns_historico = arribos_expo_ctns_historico[arribos_expo_ctns_historico['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    historico_retiros_expo = pd.read_csv('data/historico_retiros_expo.csv')
    historico_retiros_expo = historico_retiros_expo[historico_retiros_expo['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    historico_verificaciones_expo = pd.read_csv('data/historico_verificaciones_expo.csv')
    historico_verificaciones_expo = historico_verificaciones_expo[historico_verificaciones_expo['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    historico_otros_expo = pd.read_csv('data/historico_otros_expo.csv')
    historico_otros_expo = historico_otros_expo[historico_otros_expo['Cliente'].str.contains('Henn|Fulling|Forestal San')]


    return arribos_impo_historico, historico_retiros_impo, historico_verificaciones_impo, historico_otros_impo, arribos_expo_carga_historico, arribos_expo_ctns_historico, historico_retiros_expo, historico_verificaciones_expo, historico_otros_expo

def filter_data(data, start_date, end_date, date_column):
    filtered_data = data[(data[date_column] >= pd.to_datetime(start_date)) & 
                         (data[date_column] <= pd.to_datetime(end_date))]
    filtered_data[date_column] = filtered_data[date_column].dt.strftime('%d/%m/%Y')
    return filtered_data

def show_page_impo_historico():
    arribos_impo_historico, historico_retiros_impo, historico_verificaciones_impo, historico_otros_impo, arribos_expo_carga_historico, arribos_expo_ctns_historico, historico_retiros_expo, historico_verificaciones_expo, historico_otros_expo = fetch_data_impo_historico()
    
    # Convert date columns to datetime
    date_columns = {
        'arribos_impo_historico': 'Fecha',
        'historico_retiros_impo': 'Dia',
        'historico_verificaciones_impo': 'Dia',
        'historico_otros_impo': 'Dia', 
        'arribos_expo_carga_historico': 'Fecha',
        'arribos_expo_ctns_historico': 'Fecha',
        'historico_retiros_expo': 'Dia',
        'historico_verificaciones_expo': 'Dia',
        'historico_otros_expo': 'Dia' }
    for df_name, date_col in date_columns.items():
        df = locals()[df_name]
        if not df.empty:
            df[date_col] = pd.to_datetime(df[date_col])
    
    
    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        st.header(f"Histórico - Operaciones de IMPO")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_liftvan.png')
    col1, col2 = st.columns(2)

    with col1: 
        st.subheader("Arribos de contenedores")
        col1_1, col1_2, col1_3 = st.columns(3)
        with col1_1:
            start_date_arribos = st.date_input("Fecha Inicio", value=arribos_impo_historico['Fecha'].min() if not arribos_impo_historico.empty else datetime.now(), key='start_date_arribos')
            st.write(f"Fecha Inicio: {start_date_arribos.strftime('%d/%m/%Y')}")
        with col1_2:
            end_date_arribos = st.date_input("Fecha Fin", value=arribos_impo_historico['Fecha'].max() if not arribos_impo_historico.empty else datetime.now(), key='end_date_arribos')
            st.write(f"Fecha Fin: {end_date_arribos.strftime('%d/%m/%Y')}")
        filtered_data_arribos = filter_data(arribos_impo_historico, start_date_arribos, end_date_arribos, "Fecha")
        
        st.dataframe(filtered_data_arribos, hide_index=True, use_container_width=True, 
                     column_config={'e-tally': st.column_config.LinkColumn('e-tally link', display_text='\U0001F517')})

        st.subheader("Verificaciones")
        col1_4, col1_5, col1_6 = st.columns(3)
        if not historico_verificaciones_impo.empty:
            with col1_4:
                start_date_verificaciones = st.date_input("Fecha Inicio", value=historico_verificaciones_impo['Dia'].min() if not historico_verificaciones_impo.empty else datetime.now(), key='start_date_verificaciones')
                st.write(f"Fecha Inicio: {start_date_verificaciones.strftime('%d/%m/%Y')}")
            with col1_5:
                end_date_verificaciones = st.date_input("Fecha Fin", value=historico_verificaciones_impo['Dia'].max() if not historico_verificaciones_impo.empty else datetime.now(), key='end_date_verificaciones')
                st.write(f"Fecha Fin: {end_date_verificaciones.strftime('%d/%m/%Y')}")
            filtered_data_verificaciones = filter_data(historico_verificaciones_impo, start_date_verificaciones, end_date_verificaciones, "Dia")        
            st.dataframe(filtered_data_verificaciones, hide_index=True, use_container_width=True, 
                         column_config={'e-tally': st.column_config.LinkColumn('e-tally link', display_text='\U0001F517')})
        else:
            st.dataframe(historico_verificaciones_impo, hide_index=True, use_container_width=True, 
                         column_config={'e-tally': st.column_config.LinkColumn('e-tally link', display_text='\U0001F517')})

    with col2:
        st.subheader("Retiros")
        col2_1, col2_2, col2_3 = st.columns(3)
        if not historico_retiros_impo.empty:
            with col2_1:
                start_date_retiros = st.date_input("Fecha Inicio", value=historico_retiros_impo['Dia'].min(), key='start_date_retiros')
                st.write(f"Fecha Inicio: {start_date_retiros.strftime('%d/%m/%Y')}")
            with col2_2:
                end_date_retiros = st.date_input("Fecha Fin", value=historico_retiros_impo['Dia'].max(), key='end_date_retiros')
                st.write(f"Fecha Fin: {end_date_retiros.strftime('%d/%m/%Y')}")
            filtered_data_retiros = filter_data(historico_retiros_impo, start_date_retiros, end_date_retiros, "Dia") 
            st.dataframe(filtered_data_retiros, hide_index=True, use_container_width=True, 
                         column_config={'e-tally': st.column_config.LinkColumn('e-tally link', display_text='\U0001F517')})
        else:
            st.dataframe(historico_retiros_impo, hide_index=True, use_container_width=True, 
                         column_config={'e-tally': st.column_config.LinkColumn('e-tally link', display_text='\U0001F517')})

        st.subheader("Otros")
        col2_4, col2_5, col2_6 = st.columns(3)
        if not historico_otros_impo.empty:
            with col2_4:
                start_date_otros = st.date_input("Fecha Inicio", value=historico_otros_impo['Dia'].min(), key='start_date_otros')
                st.write(f"Fecha Inicio: {start_date_otros.strftime('%d/%m/%Y')}")
            with col2_5:
                end_date_otros = st.date_input("Fecha Fin", value=historico_otros_impo['Dia'].max(), key='end_date_otros')
                st.write(f"Fecha Fin: {end_date_otros.strftime('%d/%m/%Y')}")
            filtered_data_otros = filter_data(historico_otros_impo, start_date_otros, end_date_otros, "Dia")        
            st.dataframe(filtered_data_otros, hide_index=True, use_container_width=True)
        else:
            st.dataframe(historico_otros_impo, hide_index=True, use_container_width=True)

    


    st.header("Histórico - Operaciones de Expo")

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

        st.subheader("Verificaciones")
        col1_4, col1_5, col1_6 = st.columns(3)
        with col1_4:
            start_date_verificaciones = st.date_input("Fecha Inicio", value='2024-10-23', key='start_date_verificaciones')
            st.write(f"Fecha Inicio: {start_date_verificaciones.strftime('%d/%m/%Y')}")
        with col1_5:
            end_date_verificaciones = st.date_input("Fecha Fin", value='2025-12-31', key='end_date_verificaciones')
            st.write(f"Fecha Fin: {end_date_verificaciones.strftime('%d/%m/%Y')}")
        with col1_6:
            filtered_data_verificaciones = filter_data(historico_verificaciones_expo, start_date_verificaciones, end_date_verificaciones, "Dia")
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
            filtered_data_arribos_ctns = filter_data(arribos_expo_ctns_historico, start_date_arribos_ctns, end_date_arribos_ctns, "Fecha")
        st.dataframe(filtered_data_arribos_ctns, hide_index=True, use_container_width=True)

if __name__ == "__main__":
    while True:
        show_page_impo_historico
        time.sleep(60)  
        st.experimental_rerun()

