import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_trafico():
    trafico_entrega_vacio = pd.read_csv('data/trafico_entrega_vacio_historico.csv')
    trafico_carga = pd.read_csv('data/trafico_carga_historico.csv')
    return trafico_entrega_vacio, trafico_carga
    
def show_page_trafico():
    # Load data
    trafico_entrega_vacio, trafico_carga = fetch_data_trafico()

    st.markdown(
        '<p style="color: yellow; font-size: 20px;">Sección en construcción</p>',
        unsafe_allow_html=True
    )
    
    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Orden de Tráfico")
    
    st.subheader("Contenedores")
    st.dataframe(trafico_entrega_vacio, hide_index=True, use_container_width=True)

    st.subheader("Carga")
    st.dataframe(trafico_carga, hide_index=True, use_container_width=True)
    

if __name__ == "__main__":
    while True:
        show_page_trafico()
        time.sleep(60)  
        st.experimental_rerun() 

