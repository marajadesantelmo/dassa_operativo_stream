import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, delete_data, soft_delete_data
from utils import highlight

def fetch_preingreso_data():
    try: 
        preingreso_data = fetch_table_data("preingreso")
        display_data = pd.DataFrame()  # Initialize here
        if not preingreso_data.empty:
            preingreso_data = preingreso_data[preingreso_data['del'].isna()]
            preingreso_data = preingreso_data.drop(columns=['del'])
            column_names = ["id", "Cliente/Mercadería", "Nombre Chofer", "DNI Chofer", "Patente Camión", "Patente Acoplado", 
                            "Celular WhatsApp", "Remito/Permiso Embarque", "Obs/Carga/Lote/Partida", "Número Fila", "Fecha", "Hora", "Estado"]
            preingreso_data.columns = column_names
            preingreso_data['link'] = preingreso_data['Celular WhatsApp'].str.replace(" ", "").apply(
                lambda x: f"http://wa.me/549{x}" if x.isdigit() else None)
            preingreso_data['Hora'] = pd.to_datetime(preingreso_data['Hora']) - pd.Timedelta(hours=3)
            preingreso_data['Hora'] = preingreso_data['Hora'].dt.strftime('%H:%M')

            display_data = preingreso_data[["id", "Número Fila", "Hora", "Cliente/Mercadería", "Nombre Chofer", "Celular WhatsApp", "link", 
                                        "DNI Chofer","Patente Camión", "Patente Acoplado", "Remito/Permiso Embarque", "Obs/Carga/Lote/Partida", "Estado"]]
            display_data['Estado'] = display_data['Estado'].fillna('Pendiente')
            display_data.sort_values(by='Número Fila', inplace=True)
        else:
            preingreso_data = pd.DataFrame()
        
        preingreso_historico = fetch_table_data("preingreso_historico")
        if not preingreso_historico.empty:
            preingreso_historico = preingreso_historico[preingreso_historico['del'].isna()]
            preingreso_historico = preingreso_historico.drop(columns=['del'])
            preingreso_historico.columns = column_names
            preingreso_historico = preingreso_historico.drop(columns=['Estado'])
            preingreso_historico['link'] = preingreso_historico['Celular WhatsApp'].str.replace(" ", "").apply(
                lambda x: f"http://wa.me/549{x}" if x.isdigit() else None)
            preingreso_historico['Hora'] = pd.to_datetime(preingreso_historico['Hora']) - pd.Timedelta(hours=3)
            preingreso_historico['Hora'] = preingreso_historico['Hora'].dt.strftime('%H:%M')

            display_historico = preingreso_historico[["Fecha", "Número Fila", "Hora", "Cliente/Mercadería", "Nombre Chofer", "Celular WhatsApp", "link", 
                                        "DNI Chofer","Patente Camión", "Patente Acoplado", "Remito/Permiso Embarque", "Obs/Carga/Lote/Partida"]]
            display_historico.sort_values(by='Fecha', inplace=True)

    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        preingreso_data = pd.DataFrame()
        display_data = pd.DataFrame()
    return preingreso_data, display_data, display_historico

def show_page_camiones():
    st.set_page_config(page_title="Camiones - Preingreso", layout="wide")
    
    preingreso_data, display_data, display_historico = fetch_preingreso_data()

    col1, col2 = st.columns([7, 1])
    with col1:
        st.title("Camiones - Preingreso")
        st.markdown("Datos registrados por los conductores en el formulario de preingreso en el día de hoy")
    with col2:
        if not preingreso_data.empty:
            total_trucks = len(preingreso_data)
            ingresados = sum(preingreso_data['Estado'] == 'Ingresado')
            pendientes = total_trucks - ingresados
            st.metric(
                label="Camiones pendientes",
                value=f"{pendientes} / {total_trucks}",
            )
    
    if preingreso_data.empty:
        st.warning("No hay datos disponibles en la tabla de preingreso")
    else:
       
        st.dataframe(
            display_data.style.apply(highlight, axis=1).set_properties(subset=['link'], **{'width': '20px'}),
            column_config={'link': st.column_config.LinkColumn('link', display_text="\U0001F517")},
            hide_index=True, use_container_width=True
        )

        st.markdown("---")
        st.subheader("Eliminar Registro")
        
        col_delete1, col_delete2, col_delete3 = st.columns([1, 1, 2])
        
        with col_delete1:
            selected_id = st.selectbox(
                "Seleccionar registro para eliminar:",
                options=preingreso_data["id"].unique(),
                format_func=lambda x: f"ID {x} - {preingreso_data[preingreso_data['id']==x]['Nombre Chofer'].iloc[0] if not preingreso_data[preingreso_data['id']==x].empty else 'N/A'} - {preingreso_data[preingreso_data['id']==x]['Patente Camión'].iloc[0] if not preingreso_data[preingreso_data['id']==x].empty else 'N/A'}",
                key="delete_select"
            )
        
        with col_delete2:
            if st.button("Eliminar", key="delete_button", type="secondary"):
                try:
                    soft_delete_data("preingreso", selected_id)
                    st.success(f"Registro ID {selected_id} eliminado correctamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar registro: {e}")
        
        st.markdown("---")
        st.subheader("Datos Históricos")
        st.dataframe(
            display_historico.set_properties(subset=['link'], **{'width': '20px'}),
            column_config={'link': st.column_config.LinkColumn('link', display_text="\U0001F517")},
            hide_index=True, use_container_width=True
        )
