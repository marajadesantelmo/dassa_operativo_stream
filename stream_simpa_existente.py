import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight

@st.cache_data(ttl=60) 
def fetch_data_impo():
    existente_plz = pd.read_csv('data/existente_plz.csv')
    existente_plz = existente_plz[existente_plz['Cliente']=='Grupo Simpa Sa'].drop(columns=['Cliente'])
    existente_alm = pd.read_csv('data/existente_alm.csv')
    existente_alm = existente_alm[existente_alm['Cliente']=='Grupo Simpa Sa'].drop(columns=['Cliente'])
    return existente_plz, existente_alm

def show_page_existente():
    # Load data
    existente_plz, existente_alm= fetch_data_impo()

    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        st.header(f"Estado de la carga de IMPO")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_simpa.png')
    col1, col2 = st.columns(2)
    col4, col5 = st.columns(2)
    with col4:
        st.subheader("Plazoleta")
        st.dataframe(existente_plz, hide_index=True, use_container_width=True)
    with col5:
        st.subheader("Almacen")
        st.dataframe(existente_alm, hide_index=True, use_container_width=True)

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_existente()
        time.sleep(60)  
        st.experimental_rerun() 

