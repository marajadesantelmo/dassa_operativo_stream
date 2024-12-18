import streamlit as st
import stream_impo
import stream_expo
import stream_impo_historico
import stream_expo_historico
import stream_trafico
import stream_trafico_historico
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
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

USERNAMES = os.getenv("USERNAMES")
PASSWORDS = os.getenv("PASSWORDS")

def login(username, password):
    if username in USERNAMES and password in PASSWORDS:
        return True
    return False

# Login system
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.session_state['logged_in'] = True
            st.success("Usuario logeado")
        else:
            st.error("Usuario o clave invalidos")
else:
    page_selection  = option_menu(
        None,  # No menu title
        ["IMPO", "EXPO", "Tráfico", "IMPO - histórico", "EXPO - histórico", "Tráfico - histórico"],  
        icons=["arrow-down-circle", "arrow-up-circle", "arrow-right-circle", "book", "book", "book"], 
        menu_icon="cast",  
        default_index=0, 
        orientation="horizontal")

    if page_selection == "IMPO":
        stream_impo.show_page_impo()  
    elif page_selection == "EXPO":
        stream_expo.show_page_expo()
    elif page_selection == "Tráfico":
        stream_trafico.show_page_trafico()
    elif page_selection == "IMPO - histórico":
        stream_impo_historico.show_page_impo_historico()
    elif page_selection == "EXPO - histórico":
        stream_expo_historico.show_page_expo_historico()
    elif page_selection == "Tráfico - histórico":
        stream_trafico_historico.show_page_trafico_historico()
