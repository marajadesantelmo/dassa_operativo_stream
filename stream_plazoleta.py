import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight

@st.cache_data(ttl=60) 
def fetch_data_plazoleta():
    arribos = pd.read_csv('data/arribos.csv')
    arribos_semana = pd.read_csv('data/arribos_semana.csv')
    arribos_semana_pendientes = arribos_semana[arribos_semana['arribado'] == 0]
    tabla_arribos_pendientes = arribos_semana_pendientes
    arribos_por_fecha = tabla_arribos_pendientes['fecha'].value_counts().reset_index()
    arribos_por_fecha.columns = ['Fecha', 'CNTs']
    pendiente_desconsolidar = pd.read_csv('data/pendiente_desconsolidar.csv')
    existente_plz = pd.read_csv('data/existente_plz.csv')
    existente_plz = existente_plz[existente_plz['Operacion'].str.contains("-0-")] #Saco la mercaderia que esta en PLZ (solo quiero tachos)
    existente_plz_clientes = existente_plz['Cliente'].value_counts().reset_index()
    existente_plz_clientes.columns = ['Cliente', 'CTNs']
    cont_nac = pd.read_csv('data/contenedores_nacionales.csv')
    cont_nac_clientes = cont_nac['CLIENTE'].value_counts().reset_index()
    cont_nac_clientes.columns = ['Cliente', 'CTNs']
    arribos_expo_ctns = pd.read_csv('data/arribos_expo_ctns.csv')
    arribos_expo_ctns_por_fecha = arribos_expo_ctns['Fecha'].value_counts().reset_index()
    arribos_expo_ctns_por_fecha.columns = ['Fecha', 'CNTs']
    listos_para_remitir = pd.read_csv('data/listos_para_remitir.csv')
    vacios_disponibles = pd.read_csv('data/vacios_disponibles.csv')
    existente_plz_expo = pd.concat([listos_para_remitir[['Cliente', 'Contenedor']], vacios_disponibles[['Cliente', 'Contenedor']]])
    existente_plz_expo_clientes = existente_plz_expo['Cliente'].value_counts().reset_index()
    existente_plz_expo_clientes.columns = ['Cliente', 'CTNs']

    ctns_impo_plz = existente_plz.shape[0]
    ctns_expo_plz = listos_para_remitir.shape[0] + vacios_disponibles.shape[0]
    ctns_nac = cont_nac.shape[0]
    disponibles = 220 - ctns_impo_plz - ctns_expo_plz - ctns_nac
    tabla_resumen = pd.DataFrame({
        'Contenedor': ['Contenedores IMPO', 'Contenedores EXPO', 'Contenedores NACIONAL', 'Disponibles'],
        'Cantidad': [ctns_impo_plz, ctns_expo_plz, ctns_nac, disponibles]
    })
    tabla_resumen['%'] = (tabla_resumen['Cantidad'] / 220) * 100
    tabla_resumen['%'] = tabla_resumen['%'].round(0).astype(str) + '%'

    return arribos, pendiente_desconsolidar, existente_plz, existente_plz_clientes, cont_nac, cont_nac_clientes, arribos_semana, arribos_por_fecha, arribos_expo_ctns, arribos_expo_ctns_por_fecha, listos_para_remitir, vacios_disponibles, existente_plz_expo_clientes, tabla_resumen

def show_page_plazoleta():
    # Load data
    arribos, pendiente_desconsolidar, existente_plz, existente_plz_clientes, cont_nac, cont_nac_clientes, arribos_semana, arribos_por_fecha, arribos_expo_ctns, arribos_expo_ctns_por_fecha, listos_para_remitir, vacios_disponibles, existente_plz_expo_clientes, tabla_resumen = fetch_data_plazoleta()

    col_logo, col_title, col_tabla = st.columns([1, 5, 1])
    with col_logo:
        st.image('logo.png')
    with col_title:
        st.markdown("<h1 style='text-align: center;'>Estado actual de la Plazoleta</h1>", unsafe_allow_html=True)
    with col_tabla:
        st.dataframe(tabla_resumen, hide_index=True, use_container_width=True)

    col_impo, col_expo = st.columns(2)
    with col_impo:
        st.header("Contenedores IMPO")
        st.markdown("<hr>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 2, 1, 2])
        with col1:
            st.write("Pendientes de arribo")
            st.metric(label="Vacios", value=arribos.shape[0])
            st.metric(label="TD", value=arribos[arribos['Oper.'] == 'TD'].shape[0])
            st.metric(label="T", value=arribos[arribos['Oper.'] == 'T'].shape[0])
        with col2:
            st.write("Arribos pendientes por día")
            st.dataframe(arribos_por_fecha, hide_index=True, use_container_width=True)
        with col3:
            st.write("Existente en Plazoleta")
            st.metric(label="Total", value=existente_plz.shape[0])
            st.metric(label="TD", value=existente_plz[existente_plz['T-TD'] == 'TD'].shape[0])
            st.metric(label="House", value=existente_plz[existente_plz['T-TD'] != 'TD'].shape[0])
        with col4:
            st.write("Resumen por cliente")
            st.dataframe(existente_plz_clientes, hide_index=True, use_container_width=True)
    with col_expo:
        st.header("Contenedores EXPO")
        st.markdown("<hr>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 2, 1, 2])
        with col1:
            st.write("Pendientes de arribo")
            st.metric(label="Total", value=arribos_expo_ctns.shape[0])
        with col2:
            st.write("Arribos pendientes por día")
            st.dataframe(arribos_expo_ctns_por_fecha, hide_index=True, use_container_width=True)
        with col3:
            st.write("Existente en Plazoleta")
            st.metric(label="Total", value=listos_para_remitir.shape[0] + vacios_disponibles.shape[0])
            st.metric(label="Consolidado", value=listos_para_remitir.shape[0])
            st.metric(label="Vacios", value=vacios_disponibles.shape[0])
        with col4:
            st.write("Resumen por cliente")
            st.dataframe(existente_plz_expo_clientes, hide_index=True, use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Contenedores Nacional")
    col1_metric, col2_submetrics, col3_submetrics, col4_clientes = st.columns(4)
    with col1_metric:
        ctns_pendientes = cont_nac['Contenedor'].nunique()
        st.metric(label="Existente", value=ctns_pendientes)
    with col2_submetrics:
        cargados = cont_nac[cont_nac['CARGADO'].str.contains(r'\b(?:SI|si|Si)\b', regex=True, na=False)].shape[0]
        st.metric(label="Cargados", value=cargados)
        vacios = cont_nac[cont_nac['CARGADO'].str.contains(r'\b(?:NO|no|No)\b', regex=True, na=False)].shape[0]
        st.metric(label="Vacios", value=vacios)
    with col3_submetrics:
        rollos = cont_nac[cont_nac['OBSERVACION'].str.contains(r'\b(?:ROLLOS|Rollo)\b', regex=True, na=False)].shape[0]
        st.metric(label="Rollos", value=rollos)
        cueros = cont_nac[cont_nac['OBSERVACION'].str.contains(r'\b(?:CUERO|Cuero)\b', regex=True, na=False)].shape[0]
        st.metric(label="Cueros", value=cueros)
        otros = cont_nac[(~cont_nac['OBSERVACION'].str.contains(r'\b(?:ROLLOS|Rollo|CUERO|Cuero)\b', regex=True, na=False)) &
                         (cont_nac['CARGADO'].str.contains(r'\b(?:SI|si|Si)\b', regex=True, na=False))].shape[0]
        st.metric(label="Otros", value=otros)
    with col4_clientes:
        st.dataframe(cont_nac_clientes, hide_index=True, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_plazoleta()
        time.sleep(60)  
        st.experimental_rerun()

