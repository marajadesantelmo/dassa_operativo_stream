import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight
from supabase_connection import fetch_table_data, update_data, update_data_by_index

@st.cache_data(ttl=300) 
def fetch_data_trafico_andresito():
    arribos = fetch_table_data("trafico_arribos")
    arribos['Registro'] = pd.to_datetime(arribos['fecha_registro']) - pd.Timedelta(hours=3)
    arribos['Registro'] = arribos['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    arribos = arribos.drop(columns=['fecha_registro','key', 'Tiempo'], errors='ignore')
    

    arribos['Fecha'] = pd.to_datetime(arribos['Fecha'], errors='coerce')
    arribos = arribos.sort_values('Fecha')
    arribos = arribos[arribos['Fecha'] > pd.to_datetime('2025-08-10')]
    arribos['Fecha'] = arribos['Fecha'].dt.strftime('%d/%m/%Y')
    arribos['Estado_Normalizado'] = arribos['Estado'].apply(lambda x: 'Arribado' if pd.notna(x) and 'Arribado' in str(x) else x )
    cols = ['id']
    cols.append('Fecha')
    cols.extend([col for col in arribos.columns if col not in cols and col != 'Fecha'])
    arribos = arribos[cols]
    if 'Turno' in arribos.columns:
        arribos['Turno'] = arribos['Turno'].astype(str).apply(
            lambda x: x[:2] + ":" + x[2:] if len(x) >= 4 and x.isdigit() else 
                     ('0' + x[0] + ':' + x[1:] if len(x) == 3 and x.isdigit() else x)
        )


    pendiente_desconsolidar = fetch_table_data("trafico_pendiente_desconsolidar")
    pendiente_desconsolidar['Registro'] = pd.to_datetime(pendiente_desconsolidar['fecha_registro']) - pd.Timedelta(hours=3)
    pendiente_desconsolidar['Registro'] = pendiente_desconsolidar['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    pendiente_desconsolidar = pendiente_desconsolidar.drop(columns=['Peso', 'Cantidad', 'Envase', 'key', 'fecha_registro'], errors='ignore')
    arribos_expo_ctns = fetch_table_data("trafico_arribos_expo_ctns")   
    arribos_expo_ctns['Registro'] = pd.to_datetime(arribos_expo_ctns['fecha_registro']) - pd.Timedelta(hours=3)
    arribos_expo_ctns['Registro'] = arribos_expo_ctns['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    arribos_expo_ctns = arribos_expo_ctns.drop(columns=['fecha_registro', 'key'], errors='ignore')
    remisiones = fetch_table_data("trafico_remisiones")
    remisiones['Registro'] = pd.to_datetime(remisiones['fecha_registro']) - pd.Timedelta(hours=3)
    remisiones['Registro'] = remisiones['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    remisiones = remisiones.drop(columns=['fecha_registro', 'key'], errors='ignore')

    # Normalize Estado column for remisiones - treat all "Realizado" statuses as one case
    remisiones['Estado_Normalizado'] = remisiones['Estado'].apply(
        lambda x: 'Realizado' if pd.notna(x) and 'Realizado' in str(x) else x
    )

    return arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns


def show_page_trafico_andresito():
    # Load data
    arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns = fetch_data_trafico_andresito()
    
    # Get today's date in the same format as Fecha column
    today_str = datetime.now().strftime('%d/%m/%Y')
    # Get today's date in dd/MM format for Dia column in remisiones
    today_dia_str = datetime.now().strftime('%d/%m')
    
    st.warning(
        "⚠️ Esta página está en desarrollo. Algunas funcionalidades pueden no estar disponibles o no funcionar como se espera."
    )

    st.markdown(
        "<h1 style='text-align: left; color: #2c3e50; margin-bottom: 0;'>Orden de Tráfico</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div style='text-align: right; margin-top: -40px;'><a href='https://docs.google.com/spreadsheets/d/129PyI0APvtPYEYwJIsDf-Uzy2YQR-0ojj-IG2etHCYs' target='_blank'>Ver planilla histórica en Google Sheets</a></div>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # Use tabs for each main section
    tab_labels = [
        "Traslados IMPO",
        "Vacíos IMPO a devolver",
        "Retiros Vacíos EXPO",
        "Remisiones DASSA a puerto"
    ]
    tabs = st.tabs(tab_labels)

    # --- Tab 1: Traslados IMPO ---
    with tabs[0]:
        st.subheader("Desde Puerto a DASSA")

        col_table1, col_assign1 = st.columns([3, 1])
        with col_table1:
            with st.container():
                col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                with col_f1:
                    estado_options = ["Orden del día", "Todos"]
                    selected_estado = st.selectbox("Estado", estado_options, key="estado_filter_arribos")
                with col_f2:
                    contenedor_options = ['Todos'] + sorted(arribos['Contenedor'].dropna().unique().tolist()) if 'Contenedor' in arribos.columns else ['Todos']
                    selected_contenedor = st.selectbox("Contenedor", contenedor_options, key="contenedor_filter_arribos")
                with col_f3:
                    cliente_options = ['Todos'] + sorted(arribos['Cliente'].dropna().unique().tolist()) if 'Cliente' in arribos.columns else ['Todos']
                    selected_cliente = st.selectbox("Cliente", cliente_options, key="cliente_filter_arribos")
                with col_f4:
                    chofer_options = ['Todos'] + sorted(arribos['chofer'].dropna().unique().tolist()) if 'chofer' in arribos.columns else ['Todos']
                    selected_chofer = st.selectbox("Chofer", chofer_options, key="chofer_filter_arribos")
                filtered_arribos = arribos
                if selected_estado == "Orden del día":
                    filtered_arribos = filtered_arribos[
                        (~filtered_arribos["Estado_Normalizado"].str.contains("Arribado", na=False)) |
                        (filtered_arribos["Fecha"] == today_str)
                    ]
                if selected_contenedor != 'Todos':
                    filtered_arribos = filtered_arribos[filtered_arribos['Contenedor'] == selected_contenedor]
                if selected_cliente != 'Todos':
                    filtered_arribos = filtered_arribos[filtered_arribos['Cliente'] == selected_cliente]
                if selected_chofer != 'Todos':
                    filtered_arribos = filtered_arribos[filtered_arribos['chofer'] == selected_chofer]
                arribos = filtered_arribos
            
            arribos_display = arribos.copy()
            arribos_display = arribos_display.rename(columns={'Registro': 'Solicitud'})
            arribos_display['ID'] = arribos_display['id'].apply(lambda x: f"I{x:03d}")
            cols = ['ID'] + [col for col in arribos_display.columns if col != 'ID']
            arribos_display = arribos_display[cols]
            arribos_display = arribos_display.drop(columns=['id', 'Estado_Normalizado'], errors='ignore')
            st.dataframe(
                arribos_display.style.apply(highlight, axis=1),
                hide_index=True,
                use_container_width=True,
                height=400
            )
        with col_assign1:
            st.markdown("**Asignar Chofer**")
            if not arribos.empty:
                selected_arribo_id = st.selectbox(
                    "Registro:",
                    options=arribos["id"].unique(),
                    format_func=lambda x: f"ID {x} - {arribos[arribos['id']==x]['Contenedor'].iloc[0] if not arribos[arribos['id']==x].empty else 'N/A'}",
                    key="arribo_select"
                )
                chofer_name_arribos = st.text_input("Chofer:", key="chofer_arribos")
                if st.button("Asignar", key="assign_arribos"):
                    if chofer_name_arribos.strip():
                        try:
                            update_data("trafico_arribos", selected_arribo_id, {"chofer": chofer_name_arribos.strip()})
                            st.success(f"Chofer asignado al registro ID {selected_arribo_id}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al asignar chofer: {e}")
                    else:
                        st.warning("Por favor ingrese el nombre del chofer")

    # --- Tab 2: Vacíos IMPO a devolver ---
    with tabs[1]:
        st.subheader("Vacíos IMPO a devolver")
        with st.container():
            col_table2, col_assign2 = st.columns([3, 1])
            with col_table2:
                col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                with col_f1:
                    estado_options_pendiente = ["Orden del día", "Todos"]
                    selected_estado_pendiente = st.selectbox("Estado", estado_options_pendiente, key="estado_filter_pendiente")
                with col_f2:
                    contenedor_options_pendiente = ['Todos'] + sorted(pendiente_desconsolidar['Contenedor'].dropna().unique().tolist()) if 'Contenedor' in pendiente_desconsolidar.columns else ['Todos']
                    selected_contenedor_pendiente = st.selectbox("Contenedor", contenedor_options_pendiente, key="contenedor_filter_pendiente")
                with col_f3:
                    cliente_options_pendiente = ['Todos'] + sorted(pendiente_desconsolidar['Cliente'].dropna().unique().tolist()) if 'Cliente' in pendiente_desconsolidar.columns else ['Todos']
                    selected_cliente_pendiente = st.selectbox("Cliente", cliente_options_pendiente, key="cliente_filter_pendiente")
                with col_f4:
                    chofer_options_pendiente = ['Todos'] + sorted(pendiente_desconsolidar['chofer'].dropna().unique().tolist()) if 'chofer' in pendiente_desconsolidar.columns else ['Todos']
                    selected_chofer_pendiente = st.selectbox("Chofer", chofer_options_pendiente, key="chofer_filter_pendiente")

                filtered_pendiente_desconsolidar = pendiente_desconsolidar
                if selected_estado_pendiente == "Orden del día":
                    filtered_pendiente_desconsolidar = filtered_pendiente_desconsolidar[
                        (~filtered_pendiente_desconsolidar["Estado"].str.contains("Realizado", na=False)) ]
                if selected_contenedor_pendiente != 'Todos':
                    filtered_pendiente_desconsolidar = filtered_pendiente_desconsolidar[filtered_pendiente_desconsolidar['Contenedor'] == selected_contenedor_pendiente]
                if selected_cliente_pendiente != 'Todos':
                    filtered_pendiente_desconsolidar = filtered_pendiente_desconsolidar[filtered_pendiente_desconsolidar['Cliente'] == selected_cliente_pendiente]
                if selected_chofer_pendiente != 'Todos':
                    filtered_pendiente_desconsolidar = filtered_pendiente_desconsolidar[filtered_pendiente_desconsolidar['chofer'] == selected_chofer_pendiente]
                pendiente_desconsolidar = filtered_pendiente_desconsolidar
                pendiente_desconsolidar_display = pendiente_desconsolidar.copy()
                pendiente_desconsolidar_display = pendiente_desconsolidar_display.rename(columns={'Registro': 'Solicitud'})
                pendiente_desconsolidar_display['ID'] = pendiente_desconsolidar_display['id'].apply(lambda x: f"V{x:03d}")
                cols = ['ID'] + [col for col in pendiente_desconsolidar_display.columns if col != 'ID']
                pendiente_desconsolidar_display = pendiente_desconsolidar_display[cols]
                pendiente_desconsolidar_display = pendiente_desconsolidar_display.drop(columns=['id'], errors='ignore')
                st.dataframe(
                    pendiente_desconsolidar_display.style.apply(highlight, axis=1),
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )
            with col_assign2:
                st.markdown("**Asignar Chofer**")
                if not pendiente_desconsolidar.empty:
                    selected_pendiente_id = st.selectbox(
                        "Registro:",
                        options=pendiente_desconsolidar["id"].unique(),
                        format_func=lambda x: f"ID {x} - {pendiente_desconsolidar[pendiente_desconsolidar['id']==x]['Contenedor'].iloc[0] if not pendiente_desconsolidar[pendiente_desconsolidar['id']==x].empty else 'N/A'}",
                        key="pendiente_select"
                    )
                    chofer_name_pendiente = st.text_input("Chofer:", key="chofer_pendiente")
                    if st.button("Asignar", key="assign_pendiente"):
                        if chofer_name_pendiente.strip():
                            try:
                                update_data("trafico_pendiente_desconsolidar", selected_pendiente_id, {"chofer": chofer_name_pendiente.strip()})
                                st.success(f"Chofer asignado al registro ID {selected_pendiente_id}")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al asignar chofer: {e}")
                        else:
                            st.warning("Por favor ingrese el nombre del chofer")
                    st.markdown("**Asignar Fecha y Hora Fin**")
                    fecha_fin_pte = st.date_input("Fecha fin:", key="fecha_fin_pendiente")
                    hora_fin_pte = st.time_input("Hora fin:", key="hora_fin_pendiente")
                    if st.button("Asignar Fecha y Hora Fin", key="assign_fecha_fin_pendiente"):
                        if fecha_fin_pte and hora_fin_pte:
                            fecha_hora_fin_str = fecha_fin_pte.strftime("%d/%m/%Y") + " " + hora_fin_pte.strftime("%H:%M")
                            try:
                                update_data("trafico_pendiente_desconsolidar", selected_pendiente_id, {"Fecha y Hora Fin": fecha_hora_fin_str})
                                st.success(f"Fecha y Hora Fin asignada al registro ID {selected_pendiente_id}")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al asignar Fecha y Hora Fin: {e}")
                        else:
                            st.warning("Por favor seleccione fecha y hora")

    # --- Tab 3: Retiros Vacíos EXPO ---
    with tabs[2]:
        st.subheader("Retiros de Vacíos EXPO")
        with st.container():
            col_table3, col_assign3 = st.columns([3, 1])
            with col_table3:
                col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                with col_f1:
                    estado_options_expo = ["Orden del día", "Todos"]
                    selected_estado_expo = st.selectbox("Estado", estado_options_expo, key="estado_filter_expo")
                with col_f2:
                    booking_options_expo = ['Todos'] + sorted(arribos_expo_ctns['Booking'].dropna().unique().tolist()) if 'Booking' in arribos_expo_ctns.columns else ['Todos']
                    selected_booking_expo = st.selectbox("Booking", booking_options_expo, key="booking_filter_expo")
                with col_f3:
                    cliente_options_expo = ['Todos'] + sorted(arribos_expo_ctns['Cliente'].dropna().unique().tolist()) if 'Cliente' in arribos_expo_ctns.columns else ['Todos']
                    selected_cliente_expo = st.selectbox("Cliente", cliente_options_expo, key="cliente_filter_expo")
                with col_f4:
                    chofer_options_expo = ['Todos'] + sorted(arribos_expo_ctns['chofer'].dropna().unique().tolist()) if 'chofer' in arribos_expo_ctns.columns else ['Todos']
                    selected_chofer_expo = st.selectbox("Chofer", chofer_options_expo, key="chofer_filter_expo")

                filtered_arribos_expo_ctns = arribos_expo_ctns
                if selected_estado_expo == "Orden del día":
                    filtered_arribos_expo_ctns = filtered_arribos_expo_ctns[
                        (~filtered_arribos_expo_ctns["Estado"].str.contains("Realizado", na=False)) |
                        (filtered_arribos_expo_ctns["Fecha"] == today_str)
                    ]
                if selected_booking_expo != 'Todos':
                    filtered_arribos_expo_ctns = filtered_arribos_expo_ctns[filtered_arribos_expo_ctns['Booking'] == selected_booking_expo]
                if selected_cliente_expo != 'Todos':
                    filtered_arribos_expo_ctns = filtered_arribos_expo_ctns[filtered_arribos_expo_ctns['Cliente'] == selected_cliente_expo]
                if selected_chofer_expo != 'Todos':
                    filtered_arribos_expo_ctns = filtered_arribos_expo_ctns[filtered_arribos_expo_ctns['chofer'] == selected_chofer_expo]
                arribos_expo_ctns = filtered_arribos_expo_ctns
                arribos_expo_ctns_display = arribos_expo_ctns.copy()
                arribos_expo_ctns_display = arribos_expo_ctns_display.rename(columns={'Registro': 'Solicitud'})
                arribos_expo_ctns_display['ID'] = arribos_expo_ctns_display['id'].apply(lambda x: f"B{x:03d}")
                cols = ['ID'] + [col for col in arribos_expo_ctns_display.columns if col != 'ID']
                arribos_expo_ctns_display = arribos_expo_ctns_display[cols]
                arribos_expo_ctns_display = arribos_expo_ctns_display.drop(columns=['id'], errors='ignore')
                arribos_expo_ctns_display['Estado'] = arribos_expo_ctns_display['Estado'].fillna('Pendiente')
                st.dataframe(
                    arribos_expo_ctns_display.style.apply(highlight, axis=1),
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )
            with col_assign3:
                st.markdown("**Asignar Chofer**")
                if not arribos_expo_ctns.empty:
                    selected_expo_id = st.selectbox(
                        "Registro:",
                        options=arribos_expo_ctns["id"].unique(),
                        format_func=lambda x: f"ID {x} - {arribos_expo_ctns[arribos_expo_ctns['id']==x]['Booking'].iloc[0] if not arribos_expo_ctns[arribos_expo_ctns['id']==x].empty else 'N/A'}",
                        key="expo_select"
                    )
                    chofer_name_expo = st.text_input("Chofer:", key="chofer_expo")
                    if st.button("Asignar", key="assign_expo"):
                        if chofer_name_expo.strip():
                            try:
                                update_data("trafico_arribos_expo_ctns", selected_expo_id, {"chofer": chofer_name_expo.strip()})
                                st.success(f"Chofer asignado al registro ID {selected_expo_id}")
                                st.cache_data.clear()
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al asignar chofer: {e}")
                        else:
                            st.warning("Por favor ingrese el nombre del chofer")

    # --- Tab 4: Remisiones DASSA a puerto ---
    with tabs[3]:
        st.subheader("Remisiones de DASSA a puerto")
        with st.container():
            col_table4, col_assign4a = st.columns([3, 1])
            with col_table4:
                col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                with col_f1:
                    estado_options_remisiones = ["Orden del día", "Todos"]
                    selected_estado_remisiones = st.selectbox("Estado", estado_options_remisiones, key="estado_filter_remisiones")
                with col_f2:
                    contenedor_options_remisiones = ['Todos'] + sorted(remisiones['Contenedor'].dropna().unique().tolist()) if 'Contenedor' in remisiones.columns else ['Todos']
                    selected_contenedor_remisiones = st.selectbox("Contenedor", contenedor_options_remisiones, key="contenedor_filter_remisiones")
                with col_f3:
                    cliente_options_remisiones = ['Todos'] + sorted(remisiones['Cliente'].dropna().unique().tolist()) if 'Cliente' in remisiones.columns else ['Todos']
                    selected_cliente_remisiones = st.selectbox("Cliente", cliente_options_remisiones, key="cliente_filter_remisiones")
                with col_f4:
                    chofer_options_remisiones = ['Todos'] + sorted(remisiones['chofer'].dropna().unique().tolist()) if 'chofer' in remisiones.columns else ['Todos']
                    selected_chofer_remisiones = st.selectbox("Chofer", chofer_options_remisiones, key="chofer_filter_remisiones")

                filtered_remisiones = remisiones
                if selected_estado_remisiones == "Orden del día":
                    filtered_remisiones = filtered_remisiones[
                        (~filtered_remisiones["Estado_Normalizado"].str.contains("Realizado", na=False)) |
                        (filtered_remisiones["Dia"] == today_dia_str)
                    ]
                if selected_contenedor_remisiones != 'Todos':
                    filtered_remisiones = filtered_remisiones[filtered_remisiones['Contenedor'] == selected_contenedor_remisiones]
                if selected_cliente_remisiones != 'Todos':
                    filtered_remisiones = filtered_remisiones[filtered_remisiones['Cliente'] == selected_cliente_remisiones]
                if selected_chofer_remisiones != 'Todos':
                    filtered_remisiones = filtered_remisiones[filtered_remisiones['chofer'] == selected_chofer_remisiones]
                remisiones = filtered_remisiones

                remisiones_display = remisiones.copy()
                remisiones_display = remisiones_display.rename(columns={'Registro': 'Solicitud'})
                remisiones_display['ID'] = remisiones_display['id'].apply(lambda x: f"E{x:03d}")
                cols = ['ID'] + [col for col in remisiones_display.columns if col != 'ID']
                remisiones_display = remisiones_display[cols]
                remisiones_display = remisiones_display.drop(columns=['id', 'Estado_Normalizado'], errors='ignore')
                st.dataframe(
                    remisiones_display.style.apply(highlight, axis=1),
                    column_config={'e-tally': st.column_config.LinkColumn('e-tally', display_text="\U0001F517",)},
                    hide_index=True,
                    use_container_width=True,
                    height=400
                )
        with col_assign4a:
            st.markdown("**Asignar Chofer**")
            selected_remision_id = st.selectbox(
                "Registro:",
                options=remisiones["id"].unique(),
                format_func=lambda x: f"ID {x} - {remisiones[remisiones['id']==x]['Contenedor'].iloc[0] if not remisiones[remisiones['id']==x].empty else 'N/A'}",
                key="remision_select"
            )
            chofer_name_remisiones = st.text_input("Chofer:", key="chofer_remisiones")
            if st.button("Asignar", key="assign_remisiones"):
                if chofer_name_remisiones.strip():
                    try:
                        update_data("trafico_remisiones", selected_remision_id, {"chofer": chofer_name_remisiones.strip()})
                        st.success(f"Chofer asignado al registro ID {selected_remision_id}")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al asignar chofer: {e}")
                else:
                    st.warning("Por favor ingrese el nombre del chofer")
            st.markdown("**Asignar Fecha y Hora Fin**")
            fecha_fin = st.date_input("Fecha fin:", key="fecha_fin_remision")
            hora_fin = st.time_input("Hora fin:", key="hora_fin_remision")
            if st.button("Asignar Fecha y Hora Fin", key="assign_fecha_fin_remision"):
                if fecha_fin and hora_fin:
                    fecha_hora_fin_str = fecha_fin.strftime("%d/%m/%Y") + " " + hora_fin.strftime("%H:%M")
                    try:
                        update_data("trafico_remisiones", selected_remision_id, {"Fecha y Hora Fin": fecha_hora_fin_str})
                        st.success(f"Fecha y Hora Fin asignada al registro ID {selected_remision_id}")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al asignar Fecha y Hora Fin: {e}")
                else:
                    st.warning("Por favor seleccione fecha y hora")



