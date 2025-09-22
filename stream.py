import streamlit as st
st.set_page_config(page_title="Operativa DASSA", 
                   page_icon="📊", 
                   layout="wide")
import stream_impo
import stream_expo
import stream_balanza
import stream_buques
import stream_plazoleta
import stream_impo_historico
import stream_expo_historico
import stream_camiones
import stream_usuarios
import stream_trafico
import stream_trafico_andresito
import stream_trafico_andresitov2
import stream_trafico2
import stream_facturacion
import stream_choferes
import stream_ingresos_retiros
from streamlit_autorefresh import st_autorefresh
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager
import os
from supabase_connection import fetch_table_data

url_supabase = os.getenv("url_supabase")
key_supabase= os.getenv("key_supabase")

refresh_interval_ms = 300 * 1000  

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

# Apply auto-refresh only if user is not "andresito"
if st.session_state.get('logged_in', False) and st.session_state.get('username', "") != "andresito":
    count = st_autorefresh(interval=refresh_interval_ms, limit=None, key="auto-refresh")

if not st.session_state['logged_in']:
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(username, password):
            st.session_state['logged_in'] = True
            st.session_state.username = username
            cookies["logged_in"] = str(True)
            cookies["username"] = username 
            cookies.save()
            st.success("Usuario logeado")
            st.rerun()
        else:
            st.error("Usuario o clave invalidos")
else:
    es_cliente = users[users['user'] == st.session_state['username']]['clientes'].values[0] if not users[users['user'] == 'liftvan'].empty else None
    if es_cliente == "1":
        allowed_pages = ["IMPO", "EXPO", "Facturación", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "receipt", "box-arrow-right"]
    elif st.session_state['username'] in ["deposito", "francoperez", "federico", 
                        "fabian.fuentes", "marcos.avalos", "guardia"]:
        allowed_pages = ["IMPO", "EXPO", "Camiones", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "truck", "box-arrow-right"]
    elif st.session_state['username'] == "estigarribiaclaudio":
        allowed_pages = ["Ingresos y Retiros", "Logout"]
        icons = ["arrow-up-arrow-down", "box-arrow-right"]
    elif st.session_state['username'] == "trafico":
        allowed_pages = ["Tráfico", "Logout"]
        icons = ["car", "box-arrow-right"]
    elif st.session_state['username'] == "trafico2":
        allowed_pages = ["Tráfico2", "Logout"]
        icons = ["car", "box-arrow-right"]
    elif st.session_state['username'] == "andresito":
        allowed_pages = ["Andresito", "Gestión Choferes", "Logout"]
        icons = ["car", "people", "box-arrow-right"]
    elif st.session_state['username'] == "andresito2":
        allowed_pages = ["Andresitov2", "Gestión Choferes", "Logout"]
        icons = ["car", "people", "box-arrow-right"]
    elif st.session_state['username'] in ["plazoleta", "mudancera", "nicolasnunez"]:
        allowed_pages = ["IMPO", "EXPO", "Balanza", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "book", "box-arrow-right"]
    elif st.session_state['username'] in ["federico"]:
        allowed_pages = ["EXPO", "Balanza", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "book", "building", "truck", "box-arrow-right"]
    else:
        allowed_pages = ["IMPO", "EXPO", "Balanza", "Plazoleta", "Camiones", "Buques", "IMPO - histórico", "EXPO - histórico", "Gestión de usuarios", "Gestión Choferes", "Logout"]
        icons = ["arrow-down-circle", "arrow-up-circle", "book", "building", "truck", "clock-history", "clock-history", "clock-history", "people", "people", "box-arrow-right"]

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
        apply_mudanceras_filter = st.session_state['username'] in ["mudancera", "nicolasnunez"]
        stream_impo.show_page_impo(allowed_clients, apply_mudanceras_filter)  
    elif page_selection == "EXPO":
        allowed_clients = get_allowed_clients(st.session_state['username'])
        apply_mudanceras_filter = st.session_state['username'] in ["mudancera", "nicolasnunez"]
        stream_expo.show_page_expo(allowed_clients, apply_mudanceras_filter)
    elif page_selection == "Facturación":
        allowed_clients = get_allowed_clients(st.session_state['username'])
        stream_facturacion.show_page_facturacion(allowed_clients)
    elif page_selection == "Tráfico":
        stream_trafico.show_page_trafico()
    elif page_selection == "Tráfico2":
        stream_trafico2.show_page_trafico2()
    elif page_selection == "Andresito":
        stream_trafico_andresito.show_page_trafico_andresito()
    elif page_selection == "Andresitov2":
        stream_trafico_andresitov2.show_page_trafico_andresitov2()
    elif page_selection == "Gestión Choferes":
        stream_choferes.show_page_choferes()
    elif page_selection == "Balanza":
        apply_mudanceras_filter = st.session_state['username'] in ["mudancera", "nicolasnunez"]
        stream_balanza.show_page_balanza(apply_mudanceras_filter)
    elif page_selection == "Plazoleta":
        stream_plazoleta.show_page_plazoleta()
    elif page_selection == "IMPO - histórico":
        stream_impo_historico.show_page_impo_historico()
    elif page_selection == "EXPO - histórico":
        stream_expo_historico.show_page_expo_historico()
    elif page_selection == "Camiones":
        stream_camiones.show_page_camiones()
    elif page_selection == "Gestión de usuarios":
        stream_usuarios.show_page_usuarios()
    elif page_selection == "Ingresos y Retiros":
        stream_ingresos_retiros.show_page_ingresos_retiros()
    elif page_selection == "Buques":
        stream_buques.show_page_buques()

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