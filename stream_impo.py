import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight

@st.cache_data(ttl=60) 
def fetch_data_impo():
    arribos = pd.read_csv('data/arribos.csv')
    pendiente_desconsolidar = pd.read_csv('data/pendiente_desconsolidar.csv')
    verificaciones_impo = pd.read_csv('data/verificaciones_impo.csv')
    retiros_impo = pd.read_csv('data/retiros_impo.csv')
    retiros_impo['e-tally'] = retiros_impo['e-tally'].fillna("")
    retiros_impo['Salida'] = retiros_impo['Salida'].fillna("")
    otros_impo = pd.read_csv('data/otros_impo.csv')
    otros_impo = otros_impo[otros_impo['Dia'] != '-']
    existente_plz = pd.read_csv('data/existente_plz.csv')
    existente_plz['e-tally'] = existente_plz['e-tally'].fillna("")
    existente_alm = pd.read_csv('data/existente_alm.csv')
    existente_alm['e-tally'] = existente_alm['e-tally'].fillna("")
    ultima_actualizacion = pd.read_csv('data/ultima_actualizacion.csv')
    return arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo, existente_plz, existente_alm, ultima_actualizacion

def show_page_impo():
    # Load data
    arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo, existente_plz, existente_alm, ultima_actualizacion = fetch_data_impo()

    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Operaciones de IMPO a partir del {current_day}")

    col1, col2 = st.columns(2)

    with col1:
        col1_sub, col1_metric = st.columns([7, 1])
        with col1_sub:
            st.subheader("Arribos Contenedores día de hoy")
        with col1_metric:
            ctns_pendientes = arribos[(arribos['Estado'] != '-') & (~arribos['Estado'].str.contains('Arribado'))].shape[0]
            st.metric(label="CTNs pendientes", value=ctns_pendientes)
        st.dataframe(arribos.style.apply(highlight, axis=1).set_properties(subset=['Cliente'], **{'width': '20px'}), hide_index=True, use_container_width=True)

    with col2:
        col2_sub, col2_metric1, col2_mentric2 = st.columns([6, 1, 1])
        with col2_sub:
            st.subheader("Pendiente Desconsolidar y Vacios")
        with col2_metric1:
            st.metric(label="Ptes. Desco.", value=pendiente_desconsolidar[pendiente_desconsolidar['Estado'] == 'Pte. Desc.'].shape[0])
        with col2_mentric2:
            st.metric(label="Vacios", value=pendiente_desconsolidar[pendiente_desconsolidar['Estado'] == 'Vacio'].shape[0])
        st.dataframe(pendiente_desconsolidar.style.apply(highlight, axis=1).format(precision=0), hide_index=True, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        if st.session_state['username'] != "plazoleta":
            st.subheader("Verificaciones")
            st.dataframe(verificaciones_impo.style.apply(highlight, axis=1), 
                        hide_index=True, use_container_width=True)
            if not otros_impo.empty:
                st.subheader("Otros")
                st.dataframe(otros_impo.style.apply(highlight, axis=1), 
                        hide_index=True, use_container_width=True)
    with col4:
        st.subheader("Retiros")
        retiros_impo_ctn = retiros_impo[retiros_impo['Envase'] == "Contenedor"].drop(columns=['Envase'])
        if st.session_state['username'] != "plazoleta":
            retiros_impo_carga = retiros_impo[retiros_impo['Envase'] != "Contenedor"]
        st.write("Contenedores")
        st.dataframe(retiros_impo_ctn.style.apply(highlight, axis=1), 
                    column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",), 
                                    'Salida': st.column_config.LinkColumn('Salida', display_text="\U0001F517",)},
                    hide_index=True, use_container_width=True)
        if st.session_state['username'] != "plazoleta":
            st.write("Carga suelta")
            st.dataframe(retiros_impo_carga.style.apply(highlight, axis=1), 
                        column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",), 
                                        'Salida': st.column_config.LinkColumn('Salida', display_text="\U0001F517",)},
                        hide_index=True, use_container_width=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)

    st.header("Estado de la carga de IMPO")
    col4, col5 = st.columns(2)
    with col4:
        st.subheader("Plazoleta")
        st.dataframe(existente_plz, 
                    column_config={'e-tally': st.column_config.LinkColumn('e-tally', 
                                                display_text="\U0001F517",)},
                     hide_index=True, use_container_width=True)
    with col5:
        st.subheader("Almacen")
        st.dataframe(existente_alm, 
                column_config={'e-tally': st.column_config.LinkColumn('e-tally', 
                                                                    display_text="\U0001F517",)},
                hide_index=True, use_container_width=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.info(f"🕒 Última actualización: {ultima_actualizacion['hora'][0]}", icon="ℹ️")
    st.markdown("<hr>", unsafe_allow_html=True)

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_impo()
        time.sleep(60)  
        st.experimental_rerun()

