import streamlit as st
import stream_impo
import stream_expo
import stream_impo_historico
import stream_expo_historico
import stream_trafico
import stream_trafico_historico
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

USERNAMES = ["DASSA", "Facu"]
PASSWORDS = ["DASSA3", "123"]

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
    page_selection = option_menu(
            None,  # No menu title
            ["IMPO", "EXPO", "Tráfico", "IMPO - histórico", "EXPO - histórico", "Tráfico - histórico", "Logout"],  
            icons=["arrow-down-circle", "arrow-up-circle", "arrow-right-circle", "book", "book", "book", "box-arrow-right"],   
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
    elif page_selection == "Logout":
        cookies.pop("logged_in", None)
        cookies.pop("username", None)
        cookies.save()
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()
