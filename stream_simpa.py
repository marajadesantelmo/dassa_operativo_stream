import streamlit as st
import stream_simpa_existente
import stream_simpa_orden_del_dia
import stream_simpa_historico
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager
import os

# Page configurations
st.set_page_config(page_title="Operativa DASSA-Grupo Simpa", 
                   page_icon="📊", 
                   layout="wide")

refresh_interval_ms = 30 * 1000  # 30 seconds in milliseconds
count = st_autorefresh(interval=refresh_interval_ms, limit=None, key="auto-refresh")

# Estilo
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


page_selection = option_menu(
        None,  # No menu title
        ["IMPO", "EXPO", "Histórico"],  
        icons=["arrow-down-circle", "arrow-up-circle", "clock-history"],   
        menu_icon="cast",  
        default_index=0, 
        orientation="horizontal")
if page_selection == "IMPO":
    stream_simpa_existente.show_page_existente()
elif page_selection == "EXPO":
    stream_simpa_orden_del_dia.show_page_orden_del_dia()
elif page_selection == "Histórico":
    stream_simpa_historico.show_page_impo_historico()


