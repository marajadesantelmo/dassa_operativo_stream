import streamlit as st
import stream_impo
import stream_expo
import stream_impo_historico
import stream_expo_historico
import stream_trafico
import stream_trafico_historico
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
from streamlit_cookies_controller import CookieController
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

controller = CookieController()

USERNAMES=["DASSA", "Facu"]
PASSWORDS=["DASSA3", "123"]

def login(username, password):
    if username in USERNAMES and password in PASSWORDS:
        return True
    return False

logged_in_cookie = controller.get("logged_in")
username_cookie = controller.get("username")

if not logged_in_cookie:
    # Login form
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            # Set cookies to manage login state
            controller.set("logged_in", True)
            controller.set("username", username)
            st.success("Usuario logeado")
            st.rerun()
        else:
            st.error("Usuario o clave invalidos")
else:
    # User is logged in, show the main app
    page_selection  = option_menu(
        None,  # No menu title
        ["IMPO", "EXPO", "Tráfico", "IMPO - histórico", "EXPO - histórico", "Tráfico - histórico"],  
        icons=["arrow-down-circle", "arrow-up-circle", "arrow-right-circle", "book", "book", "book"], 
        menu_icon="cast",  
        default_index=0, 
        orientation="horizontal")

        # Logout button
    if st.sidebar.button("Logout", key="logout1"):
        controller.remove("logged_in")
        controller.remove("username")
        st.rerun()

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
