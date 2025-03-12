import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight

@st.cache_data(ttl=60) 
def fetch_data_impo():
    clientes_global_comex = pd.read_csv('data/clientes_global_comex.csv')
    clientes_global_comex = clientes_global_comex['apellido'].tolist()
    existente_plz = pd.read_csv('data/existente_plz.csv')
    existente_plz = existente_plz[existente_plz['Cliente'].isin(clientes_global_comex)]
    existente_alm = pd.read_csv('data/existente_alm.csv')
    existente_alm = existente_alm[existente_alm['Cliente'].isin(clientes_global_comex)]
    existente_plz = existente_plz.drop_duplicates()
    existente_alm = existente_alm.drop_duplicates()
    return existente_plz, existente_alm

def show_page_existente():
    # Load data
    existente_plz, existente_alm = fetch_data_impo()

    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        st.header(f"Estado de la carga de IMPO")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_global_comex.png')
    col4, col5 = st.columns(2)
    with col4:
        st.subheader("Plazoleta")
        st.dataframe(existente_plz, 
                     column_config={'e-tally': st.column_config.LinkColumn('e-tally link', 
                                                                          display_text='\U0001F517',)},
                     hide_index=True, use_container_width=True)
    with col5:
        st.subheader("Almacen")
        st.dataframe(existente_alm, 
                     column_config={'e-tally': st.column_config.LinkColumn('e-tally link', 
                                                                          display_text='\U0001F517',)},
                     hide_index=True, use_container_width=True)
    st.markdown("<hr>", unsafe_allow_html=True)

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_existente()
        time.sleep(60)  
        st.experimental_rerun() 

