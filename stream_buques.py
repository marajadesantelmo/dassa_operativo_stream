import streamlit as st
import pandas as pd
from datetime import datetime
from supabase_connection import fetch_table_data
from utils import highlight, generar_comprobante

@st.cache_data(ttl=60)
def fetch_data_balanza():
    apm_terminals = fetch_table_data("apm_terminals")
    apm_terminals.rename(columns={"dias_para_arribo": "Dias para arribo"}, inplace=True)
    apm_terminals.sort_values(by="Dias para arribo", inplace=True)
    itl_exolgan = fetch_table_data("itl_exolgan")
    itl_exolgan.rename(columns={"dias_para_arribo": "Dias para arribo"}, inplace=True)
    itl_exolgan.sort_values(by="Dias para arribo", inplace=True)
    dp_world = fetch_table_data("dp_world")
    dp_world.rename(columns={"dias_para_arribo": "Dias para arribo"}, inplace=True)
    dp_world.sort_values(by="Dias para arribo", inplace=True)
    return apm_terminals, itl_exolgan, dp_world


def show_page_buques(apply_mudanceras_filter=False):
    # Load data
    apm_terminals, itl_exolgan, dp_world = fetch_data_balanza()
    st.title("Estado de Buques en Terminales")
    st.markdown("---")
    st.subheader("APM Terminals")
    st.dataframe(apm_terminals)
    st.markdown("---")
    st.subheader("ITL Exolgan")
    st.dataframe(itl_exolgan, hide_index=True)
    st.markdown("---")
    st.subheader("DP World")
    st.dataframe(dp_world, hide_index=True)


# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_buques()
        time.sleep(60)  
        st.experimental_rerun()

