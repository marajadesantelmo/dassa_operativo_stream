import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight
from supabase_connection import fetch_table_data
@st.cache_data(ttl=60) 
def fetch_data_impo():
    arribos = fetch_table_data("arribos")
    arribos = arribos.sort_values(by="Turno")  # Sort by Turno
    pendiente_desconsolidar = fetch_table_data("pendiente_desconsolidar")
    verificaciones_impo = fetch_table_data("verificaciones_impo")
    retiros_impo = fetch_table_data("retiros_impo")
    retiros_impo['Dia'] = pd.to_datetime(retiros_impo['Dia'], format='%d/%m')
    retiros_impo = retiros_impo.sort_values(by="Dia")
    retiros_impo['Dia'] = retiros_impo['Dia'].dt.strftime('%d/%m')
    retiros_impo['Volumen'] = retiros_impo['Volumen'].round(0).astype(int)  # Round Volumen to integer
    otros_impo = fetch_table_data("otros_impo")
    otros_impo = otros_impo[otros_impo['Dia'] != '-']
    existente_plz = fetch_table_data("existente_plz")
    existente_alm = fetch_table_data("existente_alm")
    return arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo, existente_plz, existente_alm

@st.cache_data(ttl=60)
def fetch_last_update():
    update_log = fetch_table_data("update_log")
    if not update_log.empty:
        last_update = update_log[update_log['table_name'] == 'Arribos y existente']['last_update'].max()
        return pd.to_datetime(last_update).strftime("%d/%m/%Y %H:%M")
    return "No disponible"

def show_page_impo():
    # Load data
    arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo, existente_plz, existente_alm = fetch_data_impo()
    last_update = fetch_last_update()
    mudanceras_filter = ['Mercovan', 'Lift Van', 'Rsm', 'Fenisan', 'Moniport', 'Bymar', 'Noah']
    if st.session_state['username'] == "mudancera":
        arribos = arribos[arribos['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        pendiente_desconsolidar = pendiente_desconsolidar[pendiente_desconsolidar['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        verificaciones_impo = verificaciones_impo[verificaciones_impo['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        retiros_impo = retiros_impo[retiros_impo['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        otros_impo = otros_impo[otros_impo['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        existente_plz = existente_plz[existente_plz['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]
        existente_alm = existente_alm[existente_alm['Cliente'].str.contains('|'.join(mudanceras_filter), case=False, na=False)]


    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
        st.info(f'Última actualización: {last_update}')
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
        retiros_impo_ctn = retiros_impo[retiros_impo['Envase'] == "Contenedor"].drop(columns=['Envase', 'Cant.', 'Volumen', 'e-tally', 'Salida'])
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

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_impo()
        time.sleep(60)  
        st.experimental_rerun()

