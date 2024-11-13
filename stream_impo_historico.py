import streamlit as st
import pandas as pd

def fetch_data_impo_historico():
    arribos_impo_historico = pd.read_csv('data/arribos_impo_historico.csv')
    return arribos_impo_historico
    
def show_page_impo_historico():
    arribos_impo_historico = fetch_data_impo_historico()
    st.title("Histórico - Operaciones de IMPO")
    st.subheader("Arribos de contenedores")
    st.dataframe(arribos_impo_historico, hide_index=True, use_container_width=True)