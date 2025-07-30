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
import stream_usuarios
import stream_trafico
import stream_trafico_andresito
import stream_trafico2
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager
import os
from supabase_connection import fetch_table_data

url_supabase = os.getenv("url_supabase")
key_supabase= os.getenv("key_supabase")

refresh_interval_ms = 300 * 1000  
count = st_autorefresh(interval=refresh_interval_ms, limit=None, key="auto-refresh")

# Estilo
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

users = fetch_table_data("users")
users_clientes = fetch_table_data("users_clientes")

def login(username, password):
    for user_row in users.itertuples():
        if user_row.user == username and user_row.clave == password:
            return True
    return False

def get_allowed_clients(username):
    """Get list of clients that a user is allowed to see"""
    user_clients = users_clientes[users_clientes['user'] == username]
    if user_clients.empty:
        return None  # No restrictions, can see all clients
    return user_clients['cliente'].tolist()

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
    # Get user data to check clientes field
    user_data = None
    for user_row in users.itertuples():
        if user_row.user == st.session_state['username']:
            user_data = user_row
            break
    
    if user_data and user_data.clientes == 1:
        allowed_pages = ["IMPO", "EXPO", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "box-arrow-right"]
    elif st.session_state['username'] == "deposito":
        allowed_pages = ["IMPO", "EXPO", "Camiones", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "truck", "box-arrow-right"]
    elif st.session_state['username'] == "trafico":
        allowed_pages = ["Tráfico", "Logout"]
        icons = ["car", "box-arrow-right"]
    elif st.session_state['username'] == "trafico2":
        allowed_pages = ["Tráfico2", "Logout"]
        icons = ["car", "box-arrow-right"]
    elif st.session_state['username'] == "andresito":
        allowed_pages = ["Andresito", "Logout"]
        icons = ["car", "box-arrow-right"]
    elif st.session_state['username'] in ["plazoleta", "mudancera"]:
        allowed_pages = ["IMPO", "EXPO", "Balanza", "Plazoleta", "Camiones", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "book", "building", "truck", "box-arrow-right"]
    else:
        allowed_pages = ["IMPO", "EXPO", "Balanza", "Plazoleta", "Camiones", "IMPO - histórico", "EXPO - histórico", "Gestión de usuarios", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "book", "building", "truck", "book", "book", "people", "box-arrow-right"]

    page_selection = option_menu(
        None,  # No menu title
        allowed_pages,  
        icons=icons,
        menu_icon="cast",  
        default_index=0, 
        orientation="horizontal"
    )
    if page_selection == "IMPO":
        allowed_clients = get_allowed_clients(st.session_state['username'])
        stream_impo.show_page_impo(allowed_clients)  
    elif page_selection == "EXPO":
        allowed_clients = get_allowed_clients(st.session_state['username'])
        stream_expo.show_page_expo(allowed_clients)
    elif page_selection == "Tráfico":
        stream_trafico.show_page_trafico()
    elif page_selection == "Tráfico2":
        stream_trafico2.show_page_trafico2()
    elif page_selection == "Andresito":
        stream_trafico_andresito.show_page_trafico_andresito()
    elif page_selection == "Balanza":
        allowed_clients = get_allowed_clients(st.session_state['username'])
        stream_balanza.show_page_balanza(allowed_clients)
    elif page_selection == "Plazoleta":
        allowed_clients = get_allowed_clients(st.session_state['username'])
        stream_plazoleta.show_page_plazoleta(allowed_clients)
    elif page_selection == "IMPO - histórico":
        allowed_clients = get_allowed_clients(st.session_state['username'])
        stream_impo_historico.show_page_impo_historico(allowed_clients)
    elif page_selection == "EXPO - histórico":
        allowed_clients = get_allowed_clients(st.session_state['username'])
        stream_expo_historico.show_page_expo_historico(allowed_clients)
    elif page_selection == "Camiones":
        allowed_clients = get_allowed_clients(st.session_state['username'])
        stream_camiones.show_page_camiones(allowed_clients)
    elif page_selection == "Gestión de usuarios":
        stream_usuarios.show_page_usuarios()
    elif page_selection == "Logout":
        cookies.pop("logged_in", None)
        cookies.pop("username", None)
        cookies.save()
        st.session_state['logged_in'] = False
        st.session_state['username'] = ""
        st.rerun()

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)