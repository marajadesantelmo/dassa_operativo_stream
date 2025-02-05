import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight

@st.cache_data(ttl=60) 
def fetch_data_balanza():
    balanza = pd.read_csv('data/balanza.csv')
    balanza_impo = balanza[balanza['tipo_oper'] == 'Importacion']
    balanza_expo = balanza[balanza['tipo_oper'] == 'Exportacion']
    return balanza_impo, balanza_expo

def show_page_balanza():
    # Load data
    balanza_impo, balanza_expo = fetch_data_balanza()

    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Operaciones en balanza del {current_day}")
    st.subheader("Importación")
    columns_to_format = ['id Pesada', 'Peso Bruto', 'Peso Tara', 'Peso Neto', 'Peso Mercadería']
    st.dataframe(balanza_impo, 
            column_config={col: st.column_config.NumberColumn(col, format="%s") for col in columns_to_format},
            hide_index=True, 
            use_container_width=True)
    st.subheader("Exportación")
    st.dataframe(balanza_expo,
            column_config={col: st.column_config.NumberColumn(col, format="%s") for col in columns_to_format},
            hide_index=True, 
            use_container_width=True)
# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_balanza()
        time.sleep(60)  
        st.experimental_rerun() 

