import streamlit as st
st.set_page_config(page_title="Operativa DASSA-Henn & Cía", 
                   page_icon="📊", 
                   layout="wide")

import stream_henn_existente
import stream_henn_orden_del_dia
import stream_henn_historico
import stream_henn_facturacion
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager
import os

# Page configurations


# Estilo
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

refresh_interval_ms = 120 * 1000  # 2 minutes
count = st_autorefresh(interval=refresh_interval_ms, limit=None, key="auto-refresh")

USERNAMES = ["operativo", "administrativo"]
PASSWORDS = ["op123", "adm123"]

def login(username, password):
    if username in USERNAMES and password in PASSWORDS:
        return True
    return False

# Initialize cookies manager
cookies = EncryptedCookieManager(prefix="dassa_", password="your_secret_password")

if not cookies.ready():
    st.stop()

# Check if user is already logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = cookies.get("logged_in", False)
if 'username' not in st.session_state:
    st.session_state.username = cookies.get("username", "")

if not st.session_state['logged_in']:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.session_state['logged_in'] = True
            st.session_state.username = username
            cookies["logged_in"] = str(True)  # Convert to string
            cookies["username"] = username  # Username is already a string
            cookies.save()  # Persist the changes
            st.success("Usuario logeado")
            st.rerun()
        else:
            st.error("Usuario o clave invalidos")
else:
    if st.session_state.username == "operativo":
        pages = ["Existente", "Orden del Día", "Histórico", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "clock-history", "box-arrow-right"]
    else:
        pages = ["Existente", "Orden del Día", "Histórico", "Facturación", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "clock-history", "book", "box-arrow-right"]

    page_selection = option_menu(
            None,  # No menu title
            pages,  
            icons=icons,
            menu_icon="cast",  
            default_index=0, 
            orientation="horizontal")
    
    if page_selection == "Existente":
        stream_henn_existente.show_page_existente()
    elif page_selection == "Orden del Día":
        stream_henn_orden_del_dia.show_page_orden_del_dia()
    elif page_selection == "Histórico":
        stream_henn_historico.show_page_impo_historico()
    elif page_selection == "Facturación" and st.session_state.username != "operativo":
        stream_henn_facturacion.show_page_facturacion()
    elif page_selection == "Logout":
        cookies.pop("logged_in", None)
        cookies.pop("username", None)
        cookies.save()
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()


