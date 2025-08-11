import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, delete_data, soft_delete_data
from utils import highlight

def show_page_camiones():
    st.title("Camiones - Preingreso")
    st.markdown("Datos registrados por los conductores en el formulario de preingreso en el día de hoy")

    try: 
        preingreso_data = fetch_table_data("preingreso")
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
                                       "DNI Chofer","Patente Camión", "Patente Acoplado", "Remito/Permiso Embarque", "Obs/Carga/Lote/Partida", 'Estado']]
        
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        preingreso_data = pd.DataFrame()
        display_data = pd.DataFrame()
    
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

