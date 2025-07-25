import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight

@st.cache_data(ttl=60) 
def fetch_data():
    pendiente_consolidar = pd.read_csv('data/pendiente_consolidar.csv')
    pendiente_consolidar = pendiente_consolidar[pendiente_consolidar['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    listos_para_remitir = pd.read_csv('data/listos_para_remitir.csv')
    listos_para_remitir = listos_para_remitir[listos_para_remitir['Cliente'].str.contains('Henn|Fulling|Forestal San')]
    listos_para_remitir['e-tally'] = listos_para_remitir['e-tally'].fillna("")
    return  pendiente_consolidar, listos_para_remitir

def show_page_existente():
    # Load data
    pendiente_consolidar, listos_para_remitir = fetch_data()

    col_title, col_logo, col_simpa = st.columns([5, 1, 1])
    with col_title:
        st.header(f"Estado de la carga de EXPO")
    with col_logo:
        st.image('logo.png')
    with col_simpa:
        st.image('logo_henn.png')

    col4, col5 = st.columns(2)
    with col4:
        st.subheader("Pendiente de Consolidar")
        st.dataframe(pendiente_consolidar, hide_index=True, use_container_width=True)
    with col5:
        st.subheader("Pendiente de Remitir")
        st.dataframe(listos_para_remitir, 
                    column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",)},
                    hide_index=True, use_container_width=True)

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_existente()
        time.sleep(60)  
        st.experimental_rerun() 

