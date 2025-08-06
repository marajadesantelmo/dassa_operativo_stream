import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, delete_data

def show_page_camiones():
    st.title("Camiones - Preingreso")
    st.markdown("Datos registrados por los conductores en el formulario de preingreso en el día de hoy")

    try: 
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
        
        st.markdown("---")
        st.subheader("Eliminar registro")
        available_ids = preingreso_data["id"].unique()
        selected_id = st.selectbox(
            "Seleccionar id a eliminar:",
            options=available_ids,
            format_func=lambda x: f"id {x}"
        )
    
        if st.button("🗑️ Eliminar registro", type="secondary"):
            if 'confirm_delete' not in st.session_state:
                st.session_state.confirm_delete = False
            if not st.session_state.confirm_delete:
                st.session_state.confirm_delete = True
                st.warning(f"¿Está seguro que desea eliminar el registro con id {selected_id}?")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirmar eliminación", type="primary"):
                        try:
                            delete_data("preingreso", selected_id)
                            st.success(f"Registro con id {selected_id} eliminado correctamente")
                            st.session_state.show_confirm = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al eliminar el registro: {e}")
                            st.session_state.show_confirm = False
                
                with col2:
                    if st.button("❌ Cancelar"):
                        st.session_state.confirm_delete = False
                        st.rerun()