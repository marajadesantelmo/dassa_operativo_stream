import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight

@st.cache_data(ttl=60) 
def fetch_data_balanza():
    balanza = pd.read_csv('data/balanza.csv')
    return balanza

def show_page_balanza():
    # Load data
    balanza = fetch_data_balanza()

    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Operaciones en balanza del {current_day}")

    st.dataframe(balanza, hide_index=True, use_container_width=True)

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_balanza()
        time.sleep(60)  
        st.experimental_rerun() 

