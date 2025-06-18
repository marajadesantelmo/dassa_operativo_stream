import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data

def show_page_camiones():
    st.title("Camiones - Preingreso")
    st.markdown("Datos registrados por los conductores en el formulario de preingreso en el día de hoy.")

    # Fetch data from the "preingreso" table
    preingreso_data = fetch_table_data("preingreso")
    # Rename columns for better visualization
    preingreso_data.columns = [
        "ID",
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
        "Hora"
    ]
    preingreso_data = preingreso_data[["Número Fila", "Cliente/Mercadería", "Nombre Chofer", "Celular WhatsApp", "DNI Chofer",
        "Patente Camión", "Patente Acoplado", "Remito/Permiso Embarque", "Obs/Carga/Lote/Partida"]]

    if preingreso_data.empty:
        st.warning("No hay datos disponibles en la tabla de preingreso")
    else:
        # Display the data in a table
        st.dataframe(preingreso_data, hide_index=True, use_container_width=True)