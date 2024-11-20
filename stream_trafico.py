import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_trafico():
    arribos_vacios = pd.read_csv('data/trafico_arribos_vacios.csv')
    return arribos_vacios
    
def show_page_trafico():
    # Load data
    arribos_vacios= fetch_data_trafico()

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
    st.dataframe(arribos_vacios, hide_index=True, use_container_width=True)

    

if __name__ == "__main__":
    while True:
        show_page_trafico()
        time.sleep(60)  
        st.experimental_rerun() 

