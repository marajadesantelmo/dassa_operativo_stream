import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight

@st.cache_data(ttl=60) 
def fetch_data_plazoleta():
    arribos = pd.read_csv('data/arribos.csv')
    pendiente_desconsolidar = pd.read_csv('data/pendiente_desconsolidar.csv')
    existente_plz = pd.read_csv('data/existente_plz.csv')
    existente_plz['e-tally'] = existente_plz['e-tally'].fillna("")
    return arribos, pendiente_desconsolidar, existente_plz

def show_page_plazoleta():
    # Load data
    arribos, pendiente_desconsolidar,  existente_plz = fetch_data_plazoleta()

    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Estado actual de la Plazoleta")

    st.subheader("Contenedores Nacional")

    col1, col2, col3 = st.columns(3)

    with col1:
        col1_sub, col1_metric = st.columns([7, 1])
        with col1_sub:
            st.subheader("Arribos Contenedores")
        with col1_metric:
            ctns_pendientes = arribos[(arribos['Estado'] != '-') & (~arribos['Estado'].str.contains('Arribado'))].shape[0]
            st.metric(label="CTNs pendientes", value=ctns_pendientes)
        st.dataframe()

    with col2:
        col2_sub, col2_metric1, col2_mentric2 = st.columns([6, 1, 1])
        with col2_sub:
            st.subheader("Pendiente Desconsolidar y Vacios")
        with col2_metric1:
            st.metric(label="Ptes. Desco.", value=pendiente_desconsolidar[pendiente_desconsolidar['Estado'] == 'Pte. Desc.'].shape[0])
        with col2_mentric2:
            st.metric(label="Vacios", value=pendiente_desconsolidar[pendiente_desconsolidar['Estado'] == 'Vacio'].shape[0])

    with col3: 
        st.subheader("AGREGAR INFO")

    st.markdown("<hr>", unsafe_allow_html=True)


# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_plazoleta()
        time.sleep(60)  
        st.experimental_rerun() 

