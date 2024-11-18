import streamlit as st
import pandas as pd
from datetime import datetime
import time
from utils import highlight

def fetch_data_trafico():
    trafico = pd.read_csv('data/trafico.csv')
    return trafico
    
def show_page_trafico():
    # Load data
    trafico  = fetch_data_trafico()
    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Orden de Tráfico")
    
    st.subheader("Tráfico")
    st.dataframe(trafico.style.apply(highlight, axis=1), hide_index=True, use_container_width=True)

if __name__ == "__main__":
    while True:
        show_page_trafico()
        time.sleep(60)  
        st.experimental_rerun() 

