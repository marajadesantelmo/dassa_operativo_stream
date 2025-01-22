import streamlit as st
import stream_impo_simpa
import stream_expo_simpa
import stream_impo_historico_simpa
import stream_expo_historico_simpa
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager
import os

# Page configurations
st.set_page_config(page_title="Operativa DASSA", 
                   page_icon="📊", 
                   layout="wide")

refresh_interval_ms = 30 * 1000  # 30 seconds in milliseconds
count = st_autorefresh(interval=refresh_interval_ms, limit=None, key="auto-refresh")

# Estilo
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


page_selection = option_menu(
        None,  # No menu title
        ["IMPO", "EXPO", "Tráfico", "IMPO - histórico", "EXPO - histórico", "Tráfico - histórico"],  
        icons=["arrow-down-circle", "arrow-up-circle", "arrow-right-circle", "book", "book", "book"],   
        menu_icon="cast",  
        default_index=0, 
        orientation="horizontal")
if page_selection == "IMPO":
    stream_impo_simpa.show_page_impo()  
elif page_selection == "EXPO":
    stream_expo_simpa.show_page_expo()
elif page_selection == "IMPO - histórico":
    stream_impo_historico_simpa.show_page_impo_historico()
elif page_selection == "EXPO - histórico":
    stream_expo_historico_simpa.show_page_expo_historico()

