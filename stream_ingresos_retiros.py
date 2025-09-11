import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight, filter_dataframe_by_clients    
from supabase_connection import fetch_table_data

@st.cache_data(ttl=60) 
def fetch_data():
    arribos = fetch_table_data("arribos")
    retiros_impo = fetch_table_data("retiros_impo")
    arribos_expo_carga = fetch_table_data("arribos_expo_carga")
    arribos_expo_ctns = fetch_table_data("arribos_expo_ctns")
    remisiones = fetch_table_data("remisiones")

    try:
        arribos = arribos.sort_values(by="Turno")
        arribos['Chofer'] = arribos['Chofer'].fillna('-')
        arribos['Chofer'] = arribos['Chofer'].str.title()
        # Move Dimension column after Tipo CNT if it exists
        if 'Dimension' in arribos.columns and 'Tipo CNT' in arribos.columns:
            cols = arribos.columns.tolist()
            tipo_cnt_idx = cols.index('Tipo CNT')
            cols.remove('Dimension')
            cols.insert(tipo_cnt_idx + 1, 'Dimension')
            arribos = arribos[cols]
        
        cols = retiros_impo.columns.tolist()
        if 'Operacion' in cols:
            cols.insert(2, cols.pop(cols.index('Operacion')))
            retiros_impo = retiros_impo[cols]
        retiros_impo['Dia'] = pd.to_datetime(retiros_impo['Dia'], format='%d/%m')
        retiros_impo['Hora'] = pd.to_datetime(retiros_impo['Hora'], errors='coerce').dt.strftime('%H:%M')
        retiros_impo.sort_values(by=['Dia', 'Hora'], inplace=True)
        retiros_impo['Hora'] = retiros_impo['Hora'].astype(str).str[:5]
        retiros_impo['Hora'] = retiros_impo['Hora'].apply(lambda x: x[1:] if isinstance(x, str) and x.startswith('0') else x)
        retiros_impo['Dia'] = retiros_impo['Dia'].dt.strftime('%d/%m')
        if 'Volumen' in retiros_impo.columns:
            retiros_impo['Volumen'] = retiros_impo['Volumen'].round(0).astype(int)
        cols = retiros_impo.columns.tolist()
        if 'Hora' in cols:
            cols.insert(1, cols.pop(cols.index('Hora')))
            retiros_impo = retiros_impo[cols]
    except Exception:
        pass


    try:
        arribos_expo_carga['Fecha'] = pd.to_datetime(arribos_expo_carga['Fecha'], format='%d/%m')
        arribos_expo_carga = arribos_expo_carga.sort_values(by="Fecha")
        arribos_expo_carga['Fecha'] = arribos_expo_carga['Fecha'].dt.strftime('%d/%m')
        arribos_expo_ctns['Fecha'] = pd.to_datetime(arribos_expo_ctns['Fecha'], format='%d/%m')
        arribos_expo_ctns = arribos_expo_ctns.sort_values(by="Fecha")
        arribos_expo_ctns['Fecha'] = arribos_expo_ctns['Fecha'].dt.strftime('%d/%m')
        arribos_expo_ctns['Chofer'] = arribos_expo_ctns['Chofer'].fillna('-')
        arribos_expo_ctns['Chofer'] = arribos_expo_ctns['Chofer'].str.title()
        remisiones = remisiones[remisiones['Dia'] != '-']
        if not remisiones.empty:
            cols = remisiones.columns.tolist()
            cols.insert(2, cols.pop(cols.index('Operacion')))
            remisiones = remisiones[cols]
            remisiones['Dia'] = pd.to_datetime(remisiones['Dia'], format='%d/%m', errors='coerce')
            remisiones['Hora'] = pd.to_datetime(remisiones['Hora'], errors='coerce').dt.strftime('%H:%M')
            # Remove rows where date conversion failed
            remisiones = remisiones.dropna(subset=['Dia'])
            remisiones.sort_values(by=['Dia', 'Hora'], inplace=True)
            remisiones['Hora'] = remisiones['Hora'].astype(str).str[:5]
            remisiones['Hora'] = remisiones['Hora'].apply(lambda x: x[1:] if isinstance(x, str) and x.startswith('0') else x)
            remisiones['Dia'] = remisiones['Dia'].dt.strftime('%d/%m')
            remisiones['Chofer'] = remisiones['Chofer'].fillna('-')
            remisiones['Chofer'] = remisiones['Chofer'].str.title()
            remisiones['Volumen'] = remisiones['Volumen'].round(0).astype(int)
            cols = remisiones.columns.tolist()
            cols.insert(1, cols.pop(cols.index('Hora')))
            remisiones = remisiones[cols]
       
    except Exception:
        pass
    return arribos, retiros_impo ,arribos_expo_carga, arribos_expo_ctns, remisiones

    

@st.cache_data(ttl=60)
def fetch_last_update():
    update_log = fetch_table_data("update_log")
    if not update_log.empty:
        last_update = update_log[update_log['table_name'] == 'Arribos y existente']['last_update'].max()
        try:
            datetime_obj = pd.to_datetime(last_update)
            if pd.isna(datetime_obj):
                return "No disponible"
            return datetime_obj.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            return "No disponible"
    return "No disponible"

def show_page_ingresos_retiros(allowed_clients=None, apply_mudanceras_filter=False):
    # CARGAR DATOS
    arribos, retiros_impo ,arribos_expo_carga, arribos_expo_ctns, remisiones= fetch_data()
    last_update = fetch_last_update()

    # MOSTRAR DATOS
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
            st.subheader("Arribos Contenedores IMPO día de hoy")
        with col1_metric:
            if 'Estado' in arribos.columns:
                ctns_pendientes = arribos[(arribos['Estado'] != '-') & (~arribos['Estado'].str.contains('Arribado'))].shape[0]
            else:
                ctns_pendientes = 0
            st.metric(label="CTNs pendientes", value=ctns_pendientes)
        st.dataframe(arribos.style.apply(highlight, axis=1).set_properties(subset=['Cliente'], **{'width': '20px'}), hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Retiros IMPO")
        retiros_impo_ctn = retiros_impo[retiros_impo['Envase'] == "Contenedor"].drop(columns=['Envase', 'Cant.', 'Volumen', 'e-tally', 'Salida'])
        retiros_impo_carga = retiros_impo[retiros_impo['Envase'] != "Contenedor"]
        retiros_impo_ctnnac = retiros_impo_carga[retiros_impo_carga['Ubic.'] == 'CTNNAC']
        retiros_impo_carga = retiros_impo_carga[retiros_impo_carga['Ubic.'] != 'CTNNAC']
        st.write("Contenedores")
        st.dataframe(retiros_impo_ctn.style.apply(highlight, axis=1), 
                    hide_index=True, use_container_width=True)
        if not retiros_impo_ctnnac.empty:
            st.write("CTNs Nacionales")
            st.dataframe(retiros_impo_ctnnac.style.apply(highlight, axis=1), 
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
    st.title("Operaciones de EXPO")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Arribos Contenedores EXPO ")
        st.dataframe(arribos_expo_ctns.style.apply(highlight, axis=1).set_properties(subset=['Cliente'], **{'width': '20px'}), hide_index=True, use_container_width=True)
    with col4:
        st.subheader("Arribos Carga suelta EXPO ")
        st.dataframe(arribos_expo_carga.style.apply(highlight, axis=1).set_properties(subset=['Cliente'], **{'width': '20px'}), hide_index=True, use_container_width=True)
    st.subheader("Remisiones EXPO")
    st.dataframe(remisiones.style.apply(highlight, axis=1).set_properties(subset=['Cliente'], **{'width': '20px'}), hide_index=True, use_container_width=True)

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_ingresos_retiros()
        time.sleep(60)  
        st.experimental_rerun()

