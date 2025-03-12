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


# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_existente()
        time.sleep(60)  
        st.experimental_rerun() 

