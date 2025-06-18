import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data

def show_page_camiones():
    st.title("Camiones - Preingreso")
    st.markdown("Visualización de los datos registrados por los conductores en el formulario de preingreso.")

    # Fetch data from the "preingreso" table
    preingreso_data = fetch_table_data("preingreso")

    if preingreso_data.empty:
        st.warning("No hay datos disponibles en la tabla de preingreso")
    else:
        # Display the data in a table
        st.dataframe(preingreso_data, hide_index=True, use_container_width=True)