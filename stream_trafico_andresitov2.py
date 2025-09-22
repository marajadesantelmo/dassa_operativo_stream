import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from utils import highlight
from supabase_connection import fetch_table_data, update_data, update_data_by_index, insert_data

@st.cache_data(ttl=300) 
def fetch_data_trafico_andresitov2():
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

    pendiente_desconsolidar = fetch_table_data("traficov2_pendiente_desconsolidar")
    pendiente_desconsolidar['Registro'] = pd.to_datetime(pendiente_desconsolidar['fecha_registro']) - pd.Timedelta(hours=3)
    pendiente_desconsolidar['Registro'] = pendiente_desconsolidar['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    pendiente_desconsolidar = pendiente_desconsolidar.drop(columns=['Peso', 'Cantidad', 'Envase', 'key', 'fecha_registro'], errors='ignore')
    pendiente_desconsolidar['Vto. Vacio'] = pd.to_datetime(pendiente_desconsolidar['Vto. Vacio'], format='%d/%m', errors='coerce')
    pendiente_desconsolidar = pendiente_desconsolidar.sort_values(by='Vto. Vacio')
    pendiente_desconsolidar['Vto. Vacio'] = pendiente_desconsolidar['Vto. Vacio'].dt.strftime('%d/%m')
    arribos_expo_ctns = fetch_table_data("traficov2_arribos_ctns_expo")   
    arribos_expo_ctns['Registro'] = pd.to_datetime(arribos_expo_ctns['fecha_registro']) - pd.Timedelta(hours=3)
    arribos_expo_ctns['Registro'] = arribos_expo_ctns['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    arribos_expo_ctns = arribos_expo_ctns.drop(columns=['fecha_registro', 'key'], errors='ignore')
    arribos_expo_ctns['Fecha'] = pd.to_datetime(arribos_expo_ctns['Fecha'], format='%d/%m', errors='coerce')
    arribos_expo_ctns = arribos_expo_ctns.sort_values('Fecha')
    arribos_expo_ctns['Fecha'] = arribos_expo_ctns['Fecha'].dt.strftime('%d/%m')
    remisiones = fetch_table_data("traficov2_remisiones")
    remisiones['Registro'] = pd.to_datetime(remisiones['fecha_registro']) - pd.Timedelta(hours=3)
    remisiones['Registro'] = remisiones['Registro'].dt.strftime('%d/%m/%Y %H:%M')
    remisiones = remisiones.drop(columns=['fecha_registro', 'key'], errors='ignore')
    remisiones['Dia'] = pd.to_datetime(remisiones['Dia'], format='%d/%m', errors='coerce')
    remisiones = remisiones.sort_values('Dia')
    remisiones['Dia'] = remisiones['Dia'].dt.strftime('%d/%m')

    remisiones['Estado_Normalizado'] = remisiones['Estado'].apply(
        lambda x: 'Realizado' if pd.notna(x) and 'Realizado' in str(x) else x
    )
    choferes = fetch_table_data("choferes")
    
    # Add traficov2_otros fetching
    otros = fetch_table_data("traficov2_otros")
    if not otros.empty:
        otros['Registro'] = pd.to_datetime(otros['fecha_registro']) - pd.Timedelta(hours=3)
        otros['Registro'] = otros['Registro'].dt.strftime('%d/%m/%Y %H:%M')
        otros = otros.drop(columns=['fecha_registro'], errors='ignore')
        if 'Dia' in otros.columns:
            otros['Dia'] = pd.to_datetime(otros['Dia'], format='%d/%m', errors='coerce')
            otros = otros.sort_values('Dia')
            otros['Dia'] = otros['Dia'].dt.strftime('%d/%m')
        if 'Fecha' in otros.columns:
            otros['Fecha'] = pd.to_datetime(otros['Fecha'], format='%d/%m/%Y', errors='coerce')
            otros = otros.sort_values('Fecha', na_position='last')
            otros['Fecha'] = otros['Fecha'].dt.strftime('%d/%m/%Y')
    
    return arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns, choferes, otros

def show_page_trafico_andresitov2():
    # Load data
    arribos, pendiente_desconsolidar, remisiones, arribos_expo_ctns, choferes, otros = fetch_data_trafico_andresitov2()
    
    # Get today's date in the same format as Fecha column
    today_str = datetime.now().strftime('%d/%m/%Y')
    # Get today's date in dd/MM format for Dia column in remisiones
    today_dia_str = datetime.now().strftime('%d/%m')
    
    st.warning(
        "⚠️ Esta página está en desarrollo. Algunas funcionalidades pueden no estar disponibles o no funcionar como se espera.")
    st.markdown(
        "<h1 style='text-align: left; color: #2c3e50; margin-bottom: 0;'>Orden de Tráfico</h1>",
        unsafe_allow_html=True)
    st.markdown(
        "<div style='text-align: right; margin-top: -40px;'><a href='https://docs.google.com/spreadsheets/d/129PyI0APvtPYEYwJIsDf-Uzy2YQR-0ojj-IG2etHCYs' target='_blank'>Ver planilla histórica en Google Sheets</a></div>",
        unsafe_allow_html=True)
    st.markdown("---")

    st.subheader("I. IMPO Desde Puerto a DASSA")
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
            chofer_options = [""] + choferes['Nombre'].dropna().unique().tolist() if not choferes.empty else [""]
            chofer_name_arribos = st.selectbox(
                "Chofer:",
                options=chofer_options,
                key="chofer_arribos_select",
                index=0
            )
            
            # Allow custom input if needed
            if chofer_name_arribos == "" or st.checkbox("Ingresar otro chofer", key="custom_chofer_arribos"):
                chofer_name_arribos = st.text_input("Ingresar nombre de chofer:", key="chofer_arribos_custom")
            if st.button("Asignar", key="assign_arribos"):
                if chofer_name_arribos.strip():
                    try:
                        update_data("traficov2_arribos", selected_arribo_id, {"chofer": chofer_name_arribos.strip()})
                        st.success(f"Chofer asignado al registro ID {selected_arribo_id}")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al asignar chofer: {e}")
                else:
                    st.warning("Por favor ingrese el nombre del chofer")
            
            st.markdown("**Asignar Observaciones**")
            observaciones_arribos = st.text_area("Observaciones:", key="observaciones_arribos")
            if st.button("Asignar Observaciones", key="assign_observaciones_arribos"):
                if observaciones_arribos.strip():
                    try:
                        update_data("traficov2_arribos", selected_arribo_id, {"Observaciones": observaciones_arribos.strip()})
                        st.success(f"Observaciones asignadas al registro ID {selected_arribo_id}")
                        st.cache_data.clear()
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al asignar observaciones: {e}")
                else:
                    st.warning("Por favor ingrese las observaciones")

    st.subheader("V. Vacíos IMPO a devolver")
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
                chofer_name_pendiente = st.selectbox(
                    "Chofer:",
                    options=chofer_options,
                    key="chofer_pendiente_select",
                    index=0
                )
                
                # Allow custom input if needed
                if chofer_name_pendiente == "" or st.checkbox("Ingresar otro chofer", key="custom_chofer_pendiente"):
                    chofer_name_pendiente = st.text_input("Ingresar nombre de chofer:", key="chofer_pendiente_custom")

                if st.button("Asignar", key="assign_pendiente"):
                    if chofer_name_pendiente.strip():
                        try:
                            update_data("traficov2_pendiente_desconsolidar", selected_pendiente_id, {"chofer": chofer_name_pendiente.strip()})
                            st.success(f"Chofer asignado al registro ID {selected_pendiente_id}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al asignar chofer: {e}")
                    else:
                        st.warning("Por favor ingrese el nombre del chofer")
                st.markdown("**Asignar Observaciones**")
                observaciones_pendiente = st.text_area("Observaciones:", key="observaciones_pendiente")
                if st.button("Asignar Observaciones", key="assign_observaciones_pendiente"):
                    if observaciones_pendiente.strip():
                        try:
                            update_data("traficov2_pendiente_desconsolidar", selected_pendiente_id, {"Observaciones": observaciones_pendiente.strip()})
                            st.success(f"Observaciones asignadas al registro ID {selected_pendiente_id}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al asignar observaciones: {e}")
                    else:
                        st.warning("Por favor ingrese las observaciones")
                        
                st.markdown("**Asignar Fecha y Hora Fin**")
                fecha_fin_pte = st.date_input("Fecha fin:", key="fecha_fin_pendiente")
                hora_fin_pte = st.time_input("Hora fin:", key="hora_fin_pendiente")
                if st.button("Asignar Fecha y Hora Fin", key="assign_fecha_fin_pendiente"):
                    if fecha_fin_pte and hora_fin_pte:
                        fecha_hora_fin_str = fecha_fin_pte.strftime("%d/%m/%Y") + " " + hora_fin_pte.strftime("%H:%M")
                        try:
                            update_data("traficov2_pendiente_desconsolidar", selected_pendiente_id, {"Fecha y Hora Fin": fecha_hora_fin_str})
                            st.success(f"Fecha y Hora Fin asignada al registro ID {selected_pendiente_id}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al asignar Fecha y Hora Fin: {e}")
                    else:
                        st.warning("Por favor seleccione fecha y hora")

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
                chofer_name_expo = st.selectbox(
                    "Chofer:",
                    options=chofer_options,
                    key="chofer_expo_select",
                    index=0
                )
                
                # Allow custom input if needed
                if chofer_name_expo == "" or st.checkbox("Ingresar otro chofer", key="custom_chofer_expo"):
                    chofer_name_expo = st.text_input("Ingresar nombre de chofer:", key="chofer_expo_custom")
                if st.button("Asignar", key="assign_expo"):
                    if chofer_name_expo.strip():
                        try:
                            update_data("traficov2_arribos_ctns_expo", selected_expo_id, {"chofer": chofer_name_expo.strip()})
                            st.success(f"Chofer asignado al registro ID {selected_expo_id}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al asignar chofer: {e}")
                    else:
                        st.warning("Por favor ingrese el nombre del chofer")

                st.markdown("**Asignar Observaciones**")
                observaciones_expo = st.text_area("Observaciones:", key="observaciones_expo")
                if st.button("Asignar Observaciones", key="assign_observaciones_expo"):
                    if observaciones_expo.strip():
                        try:
                            update_data("traficov2_arribos_ctns_expo", selected_expo_id, {"Observaciones": observaciones_expo.strip()})
                            st.success(f"Observaciones asignadas al registro ID {selected_expo_id}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al asignar observaciones: {e}")
                    else:
                        st.warning("Por favor ingrese las observaciones")

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
            # Ensure Estado column exists and has no NaN values for the highlight function
            if 'Estado' not in remisiones_display.columns:
                remisiones_display['Estado'] = 'Pendiente'
            else:
                remisiones_display['Estado'] = remisiones_display['Estado'].fillna('Pendiente')
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
        chofer_name_remisiones = st.selectbox(
                    "Chofer:",
                    options=chofer_options,
                    key="chofer_remisiones_select",
                    index=0
                )
                
                # Allow custom input if needed
        if chofer_name_remisiones == "" or st.checkbox("Ingresar otro chofer", key="custom_chofer_remisiones"):
            chofer_name_remisiones = st.text_input("Ingresar nombre de chofer:", key="chofer_remisiones_custom")

        if st.button("Asignar", key="assign_remisiones"):
            if chofer_name_remisiones.strip():
                try:
                    update_data("traficov2_remisiones", selected_remision_id, {"chofer": chofer_name_remisiones.strip()})
                    st.success(f"Chofer asignado al registro ID {selected_remision_id}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al asignar chofer: {e}")
            else:
                st.warning("Por favor ingrese el nombre del chofer")
                
        st.markdown("**Asignar Observaciones**")
        observaciones_remisiones = st.text_area("Observaciones:", key="observaciones_remisiones")
        if st.button("Asignar Observaciones", key="assign_observaciones_remisiones"):
            if observaciones_remisiones.strip():
                try:
                    update_data("traficov2_remisiones", selected_remision_id, {"Observaciones trafico": observaciones_remisiones.strip()})
                    st.success(f"Observaciones asignadas al registro ID {selected_remision_id}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al asignar observaciones: {e}")
            else:
                st.warning("Por favor ingrese las observaciones")
                
        st.markdown("**Asignar Fecha y Hora Fin**")
        fecha_fin = st.date_input("Fecha fin:", key="fecha_fin_remision")
        hora_fin = st.time_input("Hora fin:", key="hora_fin_remision")
        if st.button("Asignar Fecha y Hora Fin", key="assign_fecha_fin_remision"):
            if fecha_fin and hora_fin:
                fecha_hora_fin_str = fecha_fin.strftime("%d/%m/%Y") + " " + hora_fin.strftime("%H:%M")
                try:
                    update_data("traficov2_remisiones", selected_remision_id, {"Fecha y Hora Fin": fecha_hora_fin_str})
                    st.success(f"Fecha y Hora Fin asignada al registro ID {selected_remision_id}")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al asignar Fecha y Hora Fin: {e}")
            else:
                st.warning("Por favor seleccione fecha y hora")

    # Add new "Otros" section before manual data entry
    st.subheader("Otros")
    with st.container():
        col_table5, col_assign5 = st.columns([3, 1])
        with col_table5:
            col_f1, col_f2, col_f3, col_f4 = st.columns(4)
            with col_f1:
                estado_options_otros = ["Todos"]
                if not otros.empty and 'Estado' in otros.columns:
                    estado_options_otros = ["Orden del día", "Todos"]
                selected_estado_otros = st.selectbox("Estado", estado_options_otros, key="estado_filter_otros")
            with col_f2:
                operacion_options_otros = ['Todos'] + sorted(otros['Operacion'].dropna().unique().tolist()) if not otros.empty and 'Operacion' in otros.columns else ['Todos']
                selected_operacion_otros = st.selectbox("Operación", operacion_options_otros, key="operacion_filter_otros")
            with col_f3:
                cliente_options_otros = ['Todos'] + sorted(otros['Cliente'].dropna().unique().tolist()) if not otros.empty and 'Cliente' in otros.columns else ['Todos']
                selected_cliente_otros = st.selectbox("Cliente", cliente_options_otros, key="cliente_filter_otros")
            with col_f4:
                chofer_options_otros = ['Todos'] + sorted(otros['chofer'].dropna().unique().tolist()) if not otros.empty and 'chofer' in otros.columns else ['Todos']
                selected_chofer_otros = st.selectbox("Chofer", chofer_options_otros, key="chofer_filter_otros")

            filtered_otros = otros
            if selected_estado_otros == "Orden del día" and not otros.empty and 'Estado' in otros.columns:
                filtered_otros = filtered_otros[
                    (~filtered_otros["Estado"].str.contains("Realizado", na=False)) |
                    (filtered_otros["Dia"] == today_dia_str)
                ]
            if selected_operacion_otros != 'Todos' and not otros.empty:
                filtered_otros = filtered_otros[filtered_otros['Operacion'] == selected_operacion_otros]
            if selected_cliente_otros != 'Todos' and not otros.empty:
                filtered_otros = filtered_otros[filtered_otros['Cliente'] == selected_cliente_otros]
            if selected_chofer_otros != 'Todos' and not otros.empty:
                filtered_otros = filtered_otros[filtered_otros['chofer'] == selected_chofer_otros]
            
            otros_filtered = filtered_otros
            otros_display = otros_filtered.copy()
            
            if not otros_display.empty and 'id' in otros_display.columns:
                otros_display = otros_display.rename(columns={'Registro': 'Solicitud'})
                otros_display['ID'] = otros_display['id'].apply(lambda x: f"O{x:03d}")
                cols = ['ID'] + [col for col in otros_display.columns if col != 'ID']
                otros_display = otros_display[cols]
                otros_display = otros_display.drop(columns=['id'], errors='ignore')
            
            st.dataframe(
                otros_display.style.apply(highlight, axis=1) if not otros_display.empty else otros_display,
                hide_index=True,
                use_container_width=True,
                height=400
            )
            
        with col_assign5:
            if not otros_filtered.empty and 'id' in otros_filtered.columns:
                st.markdown("**Asignar Chofer**")
                selected_otros_id = st.selectbox(
                    "Registro:",
                    options=otros_filtered["id"].unique(),
                    format_func=lambda x: f"ID {x} - {otros_filtered[otros_filtered['id']==x]['Operacion'].iloc[0] if not otros_filtered[otros_filtered['id']==x].empty else 'N/A'}",
                    key="otros_select"
                )
                chofer_name_otros = st.selectbox(
                    "Chofer:",
                    options=chofer_options,
                    key="chofer_otros_select",
                    index=0
                )
                
                # Allow custom input if needed
                if chofer_name_otros == "" or st.checkbox("Ingresar otro chofer", key="custom_chofer_otros"):
                    chofer_name_otros = st.text_input("Ingresar nombre de chofer:", key="chofer_otros_custom")

                if st.button("Asignar", key="assign_otros"):
                    if chofer_name_otros.strip():
                        try:
                            update_data("traficov2_otros", selected_otros_id, {"chofer": chofer_name_otros.strip()})
                            st.success(f"Chofer asignado al registro ID {selected_otros_id}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al asignar chofer: {e}")
                    else:
                        st.warning("Por favor ingrese el nombre del chofer")

                st.markdown("**Asignar Observaciones**")
                observaciones_otros = st.text_area("Observaciones:", key="observaciones_otros")
                if st.button("Asignar Observaciones", key="assign_observaciones_otros"):
                    if observaciones_otros.strip():
                        try:
                            update_data("traficov2_otros", selected_otros_id, {"Observaciones trafico": observaciones_otros.strip()})
                            st.success(f"Observaciones asignadas al registro ID {selected_otros_id}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al asignar observaciones: {e}")
                    else:
                        st.warning("Por favor ingrese las observaciones")
                        
                st.markdown("**Asignar Fecha y Hora Fin**")
                fecha_fin_otros = st.date_input("Fecha fin:", key="fecha_fin_otros")
                hora_fin_otros = st.time_input("Hora fin:", key="hora_fin_otros")
                if st.button("Asignar Fecha y Hora Fin", key="assign_fecha_fin_otros"):
                    if fecha_fin_otros and hora_fin_otros:
                        fecha_hora_fin_str = fecha_fin_otros.strftime("%d/%m/%Y") + " " + hora_fin_otros.strftime("%H:%M")
                        try:
                            update_data("traficov2_otros", selected_otros_id, {"Fecha y Hora Fin": fecha_hora_fin_str})
                            st.success(f"Fecha y Hora Fin asignada al registro ID {selected_otros_id}")
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al asignar Fecha y Hora Fin: {e}")
                    else:
                        st.warning("Por favor seleccione fecha y hora")

    # Manual Data Entry Section
    st.markdown("---")
    st.subheader("Agregar Registro Manual")
    
    # Table selection
    table_options = {
        "Traslados IMPO": "traficov2_arribos",
        "Vacíos IMPO a devolver": "traficov2_pendiente_desconsolidar", 
        "Retiros Vacíos EXPO": "traficov2_arribos_ctns_expo",
        "Remisiones DASSA a puerto": "traficov2_remisiones",
        "Otros": "traficov2_otros"
    }
    
    selected_table_name = st.selectbox(
        "Seleccionar tabla para agregar datos:",
        options=list(table_options.keys()),
        key="table_selection"
    )
    
    selected_table = table_options[selected_table_name]
    
    # Get the corresponding dataframe
    if selected_table == "traficov2_arribos":
        df_columns = arribos.columns.tolist()
    elif selected_table == "traficov2_pendiente_desconsolidar":
        df_columns = pendiente_desconsolidar.columns.tolist()
    elif selected_table == "traficov2_arribos_ctns_expo":
        df_columns = arribos_expo_ctns.columns.tolist()
    elif selected_table == "traficov2_otros":
        if not otros.empty:
            df_columns = otros.columns.tolist()
        else:
            # Provide default columns for empty otros table based on database schema
            df_columns = [
                'id', 'Dia', 'Hora', 'Tipo Turno', 'Operacion', 'Cliente', 'Contenedor', 
                'chofer', 'Fecha y Hora Fin', 'Observaciones', 'Terminal', 'Dimension', 
                'Entrega', 'Cantidad', 'Fecha', 'Origen', 'Observaciones trafico', 
                'Valor', 'fecha_registro'
            ]
    else:  # traficov2_remisiones
        df_columns = remisiones.columns.tolist()
    
    # Remove id and auto-generated columns
    excluded_columns = ['id', 'Registro', 'Solicitud', 'fecha_registro', 'key', 'Estado_Normalizado']
    form_columns = [col for col in df_columns if col not in excluded_columns]
    
    st.markdown(f"**Agregar nuevo registro a: {selected_table_name}**")
    
    with st.form(f"add_record_{selected_table}"):
        form_data = {}
        
        # Create form fields for each column
        col1, col2 = st.columns(2)
        
        for i, column in enumerate(form_columns):
            with col1 if i % 2 == 0 else col2:
                if column in ['Fecha', 'Dia']:
                    if column == 'Fecha':
                        form_data[column] = st.date_input(f"{column}:", key=f"form_{column}_{selected_table}")
                    else:  # Dia column for remisiones
                        form_data[column] = st.text_input(f"{column} (DD/MM):", key=f"form_{column}_{selected_table}")
                elif column in ['Turno', 'Hora']:
                    form_data[column] = st.time_input(f"{column}:", key=f"form_{column}_{selected_table}")
                elif column in ['Estado', 'Cliente', 'Contenedor', 'Booking', 'chofer', 'Valor']:
                    form_data[column] = st.text_input(f"{column}:", key=f"form_{column}_{selected_table}")
                elif column in ['Peso', 'Cantidad']:
                    form_data[column] = st.number_input(f"{column}:", min_value=0.0, key=f"form_{column}_{selected_table}")
                elif 'tally' in column.lower():
                    form_data[column] = st.text_input(f"{column} (URL):", key=f"form_{column}_{selected_table}")
                else:
                    form_data[column] = st.text_input(f"{column}:", key=f"form_{column}_{selected_table}")
        
        submitted = st.form_submit_button("Agregar Registro")
        
        if submitted:
            # Prepare data for insertion
            insert_data_dict = {}
            
            for column, value in form_data.items():
                if value is not None and value != "":
                    if column == 'Fecha' and hasattr(value, 'strftime'):
                        insert_data_dict[column] = value.strftime('%d/%m/%Y')
                    elif column in ['Turno', 'Hora'] and hasattr(value, 'strftime'):
                        insert_data_dict[column] = value.strftime('%H%M') if column == 'Turno' else value.strftime('%H:%M')
                    else:
                        insert_data_dict[column] = str(value)
            
            # Add timestamp for registro
            current_time = datetime.now()
            insert_data_dict['fecha_registro'] = current_time.isoformat()
            
            try:
                insert_data(selected_table, insert_data_dict)
                st.success(f"Registro agregado exitosamente a {selected_table_name}")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Error al agregar registro: {e}")



