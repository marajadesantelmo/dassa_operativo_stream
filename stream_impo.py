import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight, filter_dataframe_by_clients    
from supabase_connection import fetch_table_data
import plotly.express as px
@st.cache_data(ttl=60) 
def fetch_data_impo():
    arribos = fetch_table_data("arribos")
    pendiente_desconsolidar = fetch_table_data("pendiente_desconsolidar")
    verificaciones_impo = fetch_table_data("verificaciones_impo")
    retiros_impo = fetch_table_data("retiros_impo")
    otros_impo = fetch_table_data("otros_impo")
    existente_plz = fetch_table_data("existente_plz")
    existente_alm = fetch_table_data("existente_alm")
    grafico_arribos_impo = fetch_table_data("grafico_arribos_impo")
    grafico_verificaciones_impo = fetch_table_data("grafico_verificaciones_impo")
    grafico_retiros_impo = fetch_table_data("grafico_retiros_impo")
    try:
        arribos = arribos.sort_values(by="Turno")
        arribos['Chofer'] = arribos['Chofer'].fillna('-')
        arribos['Chofer'] = arribos['Chofer'].str.title()
        # Move Dimension column after Tipo CNT if it exists
        cols = arribos.columns.tolist()
        tipo_cnt_idx = cols.index('Tipo CNT')
        cols.remove('Dimension')
        cols.insert(tipo_cnt_idx + 1, 'Dimension')
        arribos = arribos[cols]
        verificaciones_impo = verificaciones_impo.drop(columns=['Hora'])
        pendiente_desconsolidar['Vto. Vacio'] = pd.to_datetime(pendiente_desconsolidar['Vto. Vacio'], format='%d/%m', errors='coerce')
        pendiente_desconsolidar = pendiente_desconsolidar.sort_values(by='Vto. Vacio')
        pendiente_desconsolidar['Vto. Vacio'] = pendiente_desconsolidar['Vto. Vacio'].dt.strftime('%d/%m')
        pendiente_desconsolidar['Chofer'] = pendiente_desconsolidar['Chofer'].fillna('-')
        pendiente_desconsolidar['Chofer'] = pendiente_desconsolidar['Chofer'].str.title()
        cols = verificaciones_impo.columns.tolist()
        cols.insert(2, cols.pop(cols.index('Operacion')))
        verificaciones_impo = verificaciones_impo[cols]
        cols = retiros_impo.columns.tolist()
        cols.insert(2, cols.pop(cols.index('Operacion')))
        retiros_impo = retiros_impo[cols]
        retiros_impo['Dia'] = pd.to_datetime(retiros_impo['Dia'], format='%d/%m')
        retiros_impo['Hora'] = pd.to_datetime(retiros_impo['Hora'], errors='coerce').dt.strftime('%H:%M')
        retiros_impo.sort_values(by=['Dia', 'Hora'], inplace=True)
        retiros_impo['Hora'] = retiros_impo['Hora'].astype(str).str[:5]
        retiros_impo['Hora'] = retiros_impo['Hora'].apply(lambda x: x[1:] if isinstance(x, str) and x.startswith('0') else x)
        retiros_impo['Dia'] = retiros_impo['Dia'].dt.strftime('%d/%m')
        retiros_impo['Volumen'] = retiros_impo['Volumen'].round(0).astype(int)
        cols = retiros_impo.columns.tolist()
        cols.insert(1, cols.pop(cols.index('Hora')))
        retiros_impo = retiros_impo[cols]
        otros_impo = otros_impo[otros_impo['Dia'] != '-']
    except Exception:
        pass

    return arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo, existente_plz, existente_alm, grafico_arribos_impo, grafico_verificaciones_impo, grafico_retiros_impo

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

def show_page_impo(allowed_clients=None, apply_mudanceras_filter=False):
    # Load data
    arribos, pendiente_desconsolidar, verificaciones_impo, retiros_impo, otros_impo, existente_plz, existente_alm, grafico_arribos_impo, grafico_verificaciones_impo, grafico_retiros_impo= fetch_data_impo()
    last_update = fetch_last_update()
    
    # Apply client filtering first
    if allowed_clients is not None:
        arribos = filter_dataframe_by_clients(arribos, allowed_clients)
        pendiente_desconsolidar = filter_dataframe_by_clients(pendiente_desconsolidar, allowed_clients)
        verificaciones_impo = filter_dataframe_by_clients(verificaciones_impo, allowed_clients)
        retiros_impo = filter_dataframe_by_clients(retiros_impo, allowed_clients)
        otros_impo = filter_dataframe_by_clients(otros_impo, allowed_clients)
        existente_plz = filter_dataframe_by_clients(existente_plz, allowed_clients)
        existente_alm = filter_dataframe_by_clients(existente_alm, allowed_clients)
    
    # Apply mudanceras filter if needed
    if apply_mudanceras_filter:
        mudanceras_filter = ['Mercovan', 'Lift Van', 'Edelweiss',  'Rsm', 'Fenisan', 'Moniport', 'Bymar', 'Noah']
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
            if 'Estado' in arribos.columns:
                ctns_pendientes = arribos[(arribos['Estado'] != '-') & (~arribos['Estado'].str.contains('Arribado'))].shape[0]
            else:
                ctns_pendientes = 0
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
            if not verificaciones_impo.empty:
                verificaciones_impo_ctn = verificaciones_impo[verificaciones_impo['Envase'] == "Contenedor"]
                verificaciones_impo_carga = verificaciones_impo[verificaciones_impo['Envase'] != "Contenedor"]
                if not verificaciones_impo_ctn.empty:
                    st.write("Contenedores")
                    st.dataframe(verificaciones_impo_ctn.style.apply(highlight, axis=1), 
                                hide_index=True, use_container_width=True)
                if not verificaciones_impo_carga.empty:
                    st.write("Carga suelta")
                    st.dataframe(verificaciones_impo_carga.style.apply(highlight, axis=1), 
                                hide_index=True, use_container_width=True)
                if not otros_impo.empty:
                    st.subheader("Otros")
                    st.dataframe(otros_impo.style.apply(highlight, axis=1), 
                            hide_index=True, use_container_width=True)
    with col4:
        st.subheader("Retiros")
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

    if st.session_state['username'] == "DASSA":
        st.header("Estadisticas IMPO")
        st.subheader("Operaciones con Contenedores")
        col1_grafico, col2_grafico = st.columns(2)
        with col1_grafico:
            grafico_arribos_impo['Fecha'] = pd.to_datetime(grafico_arribos_impo['Fecha'])
            grafico_arribos_impo = grafico_arribos_impo.sort_values('Fecha')
            grafico_arribos_impo['Fecha'] = grafico_arribos_impo['Fecha'].dt.strftime('%d/%m')
            fig = px.bar(
            grafico_arribos_impo,
            x='Fecha',
            y='Arribos',
            color='Estado',
            title='Arribos CTNs por día',
            color_discrete_map={
                'Arribado': '#4CAF50', 'Pendiente': '#FFA500'})

            fig.update_layout(
            legend_title='Estado',
            barmode='stack',
            title_font_size=20,
            yaxis=dict(range=[0, 45]),  # Set y-axis max value to 45
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))                
            st.plotly_chart(fig, use_container_width=True)

            grafico_retiros_impo['Fecha'] = pd.to_datetime(grafico_retiros_impo['Fecha'])
            grafico_retiros_impo = grafico_retiros_impo.sort_values('Fecha')
            grafico_retiros_impo['Fecha'] = grafico_retiros_impo['Fecha'].dt.strftime('%d/%m')
            grafico_retiros_impo_ctns = grafico_retiros_impo[grafico_retiros_impo['Envase'] == "Contenedor"]
            fig3 = px.bar(
            grafico_retiros_impo_ctns,
            x='Fecha',
            y='Retiros',
            color='Estado',
            title='Retiros CTNs por día',
            color_discrete_map={'Realizado': '#4CAF50', 'Pendiente': '#FFA500'})
            fig3.update_layout(
            legend_title='Estado',
            barmode='stack',
            title_font_size=20,
            yaxis=dict(range=[0, 45]),  # Set y-axis max value to 45
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))
            st.plotly_chart(fig3, use_container_width=True)

        with col2_grafico:
            grafico_verificaciones_impo['Fecha'] = pd.to_datetime(grafico_verificaciones_impo['Fecha'])
            grafico_verificaciones_impo = grafico_verificaciones_impo.sort_values('Fecha')
            grafico_verificaciones_impo['Fecha'] = grafico_verificaciones_impo['Fecha'].dt.strftime('%d/%m')
            grafico_verificaciones_impo_ctns = grafico_verificaciones_impo[grafico_verificaciones_impo['Envase'] == "Contenedor"]
            fig2 = px.bar(
            grafico_verificaciones_impo_ctns,
            x='Fecha',
            y='Verificaciones IMPO',
            color='Estado',
            title='Verificaciones CTNs por día',
            color_discrete_map={'Realizado': '#4CAF50', 'Pendiente': '#FFA500'})

            fig2.update_layout(
            legend_title='Estado',
            barmode='stack',
            title_font_size=20,
            yaxis=dict(range=[0, 45]),  # Set y-axis max value to 45
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ))                
            st.plotly_chart(fig2, use_container_width=True)


# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_impo()
        time.sleep(60)  
        st.experimental_rerun()

