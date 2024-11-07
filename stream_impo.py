import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight
@st.cache_data(ttl=60) 
def fetch_data_impo():
    arribos = pd.read_csv('data/arribos.csv')
    pendiente_desconsolidar = pd.read_csv('data/pendiente_desconsolidar.csv')
    verificaciones_impo = pd.read_csv('data/verificaciones_impo.csv')
    retiros_impo = pd.read_csv('data/retiros_impo.csv')
    otros_impo = pd.read_csv('data/otros_impo.csv')
    return arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo

def show_page_impo():
    # Load data
    arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo = fetch_data_impo()

    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Operaciones de IMPO a partir del {current_day}")

    # Create two columns
    col1, col2 = st.columns(2)

    # Column 1: Arribos
    with col1:
        st.header("Arribos Contenedores")
        st.dataframe(arribos.style.apply(highlight, axis=1).set_properties(subset=['Cliente'], **{'width': '20px'}), hide_index=True, use_container_width=True)

    # Column 2: Pendiente Desconsolidar
    with col2:
        st.header("Pendiente Desconsolidar y Vacios")
        st.dataframe(pendiente_desconsolidar.style.apply(highlight, axis=1).format(precision=0), hide_index=True, use_container_width=True)

    st.header("Turnos")
    col3, col4 = st.columns(2)
    with col3:
        st.header("Verificaciones")
        st.dataframe(verificaciones_impo.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)
        st.header("Otros")
        st.dataframe(otros_impo.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

    with col4:
        st.header("Retiros")
        st.dataframe(retiros_impo.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)


# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_impo()
        time.sleep(60)  
        st.experimental_rerun() 

