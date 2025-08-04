import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, delete_data

def show_page_camiones():
    st.title("Camiones - Preingreso")
    st.markdown("Datos registrados por los conductores en el formulario de preingreso en el día de hoy.")

    try: 
        preingreso_data = fetch_table_data("preingreso")
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
        "Hora"]

        preingreso_data['link'] = preingreso_data['Celular WhatsApp'].str.replace(" ", "").apply(
            lambda x: f"http://wa.me/549{x}" if x.isdigit() else None)
        
        # Convert Hora to datetime, subtract 3 hours, and format as hh:mm
        preingreso_data['Hora'] = pd.to_datetime(preingreso_data['Hora']) - pd.Timedelta(hours=3)
        preingreso_data['Hora'] = preingreso_data['Hora'].dt.strftime('%H:%M')

        # Reorder columns for display
        display_data = preingreso_data[["ID", "Número Fila", "Hora", "Cliente/Mercadería", "Nombre Chofer", "Celular WhatsApp", "link", 
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
        
        # Add deletion functionality
        st.markdown("---")
        st.subheader("Eliminar registro")
        
        # Create selectbox with available row numbers
        available_rows = preingreso_data["Número Fila"].unique()
        selected_row = st.selectbox(
            "Seleccionar número de fila a eliminar:",
            options=available_rows,
            format_func=lambda x: f"Fila {x}"
        )
        
        if st.button("🗑️ Eliminar registro", type="secondary"):
            # Show confirmation dialog
            if 'confirm_delete' not in st.session_state:
                st.session_state.confirm_delete = False
            
            if not st.session_state.confirm_delete:
                st.session_state.confirm_delete = True
                st.warning(f"¿Está seguro que desea eliminar la fila {selected_row}?")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar eliminación", type="primary"):
                        try:
                            # Find the record ID for the selected row number
                            record_to_delete = preingreso_data[preingreso_data["Número Fila"] == selected_row]
                            if not record_to_delete.empty:
                                record_id = record_to_delete.iloc[0]["ID"]
                                delete_data("preingreso", record_id)
                                st.success(f"Registro de la fila {selected_row} eliminado correctamente")
                                st.session_state.confirm_delete = False
                                st.rerun()
                            else:
                                st.error("No se encontró el registro a eliminar")
                        except Exception as e:
                            st.error(f"Error al eliminar el registro: {e}")
                        st.session_state.confirm_delete = False
                
                with col2:
                    if st.button("❌ Cancelar"):
                        st.session_state.confirm_delete = False
                        st.rerun()