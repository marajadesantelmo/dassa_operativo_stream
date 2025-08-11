import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, delete_data

def show_page_camiones():
    st.title("Camiones - Preingreso")
    st.markdown("Datos registrados por los conductores en el formulario de preingreso en el día de hoy")

    try: 
        if not preingreso_data.empty:
            preingreso_data = fetch_table_data("preingreso")
            preingreso_data.columns = [
            "id",
            "Cliente/Mercadería",
            "Nombre Chofer",
            "DNI Chofer",
            "Patente Camión",
            "Patente Acoplado",
            "Celular WhatsApp",
            "Remito/Permiso Embarque",
            "Obs/Carga/Lote/Partida",
            "Número Fila",
            "Fecha",
            "Hora"]
            preingreso_data['link'] = preingreso_data['Celular WhatsApp'].str.replace(" ", "").apply(
                lambda x: f"http://wa.me/549{x}" if x.isdigit() else None)
            preingreso_data['Hora'] = pd.to_datetime(preingreso_data['Hora']) - pd.Timedelta(hours=3)
            preingreso_data['Hora'] = preingreso_data['Hora'].dt.strftime('%H:%M')

            display_data = preingreso_data[["id", "Número Fila", "Hora", "Cliente/Mercadería", "Nombre Chofer", "Celular WhatsApp", "link", 
                                       "DNI Chofer","Patente Camión", "Patente Acoplado", "Remito/Permiso Embarque", "Obs/Carga/Lote/Partida"]]
        
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        preingreso_data = pd.DataFrame()
        display_data = pd.DataFrame()
    
    if preingreso_data.empty:
        st.warning("No hay datos disponibles en la tabla de preingreso")
    else:
        # Display the data in a table with WhatsApp links
        st.dataframe(
            display_data.style.set_properties(subset=['link'], **{'width': '20px'}),
            column_config={'link': st.column_config.LinkColumn('link', display_text="\U0001F517")},
            hide_index=True, use_container_width=True
        )
        
