import streamlit as st
st.set_page_config(page_title="Seguimiento de mudanzas YPF - Liftvan", 
                   page_icon="📊", 
                   layout="wide")

import stream_liftvan_ypf_impo
import stream_liftvan_ypf_expo
import stream_liftvan_ypf_nac
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
    
    pages = ["Importación", "Exportación", "Nacionales", "Logout"]
    icons = ["arrow-down-circle", "arrow-up-circle", "clock-history", "box-arrow-right"]

    page_selection = option_menu(
            None,  # No menu title
            pages,  
            icons=icons,
            menu_icon="cast",  
            default_index=0, 
            orientation="horizontal")
    
    if page_selection == "Importación":
        stream_liftvan_ypf_impo.show_page_liftvan_ypf_impo()
    elif page_selection == "Exportación":
        stream_liftvan_ypf_expo.show_page_liftvan_ypf_expo()
    elif page_selection == "Nacionales":
        stream_liftvan_ypf_nac.show_page_liftvan_ypf_nac()
    elif page_selection == "Logout":
        cookies.pop("logged_in", None)
        cookies.pop("username", None)
        cookies.save()
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()


