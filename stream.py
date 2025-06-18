import streamlit as st
st.set_page_config(page_title="Operativa DASSA", 
                   page_icon="📊", 
                   layout="wide")
import stream_impo
import stream_expo
import stream_balanza
import stream_plazoleta
import stream_impo_historico
import stream_expo_historico
import stream_camiones
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager
import os

url_supabase = os.getenv("url_supabase")
key_supabase= os.getenv("key_supabase")

refresh_interval_ms = 60 * 1000  # 30 seconds in milliseconds
count = st_autorefresh(interval=refresh_interval_ms, limit=None, key="auto-refresh")

# Estilo
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

USERNAMES = ["DASSA", "Facu", "deposito", "plazoleta", "mudancera"]
PASSWORDS = ["DASSA3", "123", "depodassa", "plazoletadassa", "mudanceradassa"]

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
    if st.session_state['username'] == "deposito":
        allowed_pages = ["IMPO", "EXPO", "Camiones", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "truck", "box-arrow-right"]
    elif st.session_state['username'] in ["plazoleta", "mudancera"]:
        allowed_pages = ["IMPO", "EXPO", "Balanza", "Plazoleta", "Camiones", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "scales", "building", "truck", "box-arrow-right"]
    else:
        allowed_pages = ["IMPO", "EXPO", "Balanza", "Plazoleta", "Camiones", "IMPO - histórico", "EXPO - histórico", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "scales", "building", "truck", "book", "book", "box-arrow-right"]

    page_selection = option_menu(
        None,  # No menu title
        allowed_pages,  
        icons=icons,
        menu_icon="cast",  
        default_index=0, 
        orientation="horizontal"
    )
    if page_selection == "IMPO":
        stream_impo.show_page_impo()  
    elif page_selection == "EXPO":
        stream_expo.show_page_expo()
    elif page_selection == "Balanza":
         stream_balanza.show_page_balanza()
    elif page_selection == "Plazoleta":
         stream_plazoleta.show_page_plazoleta()
    elif page_selection == "IMPO - histórico":
        stream_impo_historico.show_page_impo_historico()
    elif page_selection == "EXPO - histórico":
        stream_expo_historico.show_page_expo_historico()
    elif page_selection == "Camiones":
        stream_camiones.show_page_camiones()
    elif page_selection == "Logout":
        cookies.pop("logged_in", None)
        cookies.pop("username", None)
        cookies.save()
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()
