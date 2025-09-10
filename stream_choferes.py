import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
from utils import highlight
from supabase_connection import fetch_table_data, update_data, update_data_by_index, insert_data

@st.cache_data(ttl=300) 
def fetch_data_trafico_andresito():
    choferes = fetch_table_data("trafico_arribos")
    return choferes

@st.cache_data(ttl=300) 
def fetch_data_choferes():
    choferes = fetch_table_data("choferes")
    return choferes

def generate_chofer_code(tipo, existing_codes):
    """Generate next available code for chofer type"""
    prefix = {'Andresito': 'C', 'Fletero': 'F', 'Transporte': 'T'}[tipo]
    existing_numbers = []
    
    for code in existing_codes:
        if code.startswith(prefix) and len(code) > 1:
            try:
                num = int(code[1:])
                existing_numbers.append(num)
            except ValueError:
                continue
    
    next_number = max(existing_numbers, default=0) + 1
    return f"{prefix}{next_number:03d}"

def format_whatsapp_link(phone_number):
    """Convert phone number to WhatsApp link format"""
    if phone_number and str(phone_number).isdigit():
        clean_number = str(phone_number).replace(" ", "").replace("-", "")
        return f"http://wa.me/549{clean_number}"
    return None

def show_chofer_table(df_filtered, tipo):
    """Display chofer table with edit functionality"""
    if df_filtered.empty:
        st.info(f"No hay choferes de tipo {tipo} registrados")
        return
    
    # Display table
    display_df = df_filtered.copy()
    display_df['link'] = display_df['Whatsapp'].apply(lambda x: x if x and x.startswith('http') else None)
    
    st.dataframe(
        display_df[['Codigo', 'Nombre', 'DNI', 'Patente', 'Semi', 'Whatsapp', 'link', 'Transporte']].style.apply(highlight, axis=1),
        column_config={
            'link': st.column_config.LinkColumn('WhatsApp', display_text="\U0001F517"),
            'Codigo': 'Código',
            'Nombre': 'Nombre',
            'DNI': 'DNI', 
            'Patente': 'Patente',
            'Semi': 'Semi',
            'Whatsapp': 'WhatsApp',
            'Transporte': 'Transporte'
        },
        hide_index=True,
        use_container_width=True
    )
    
    # Edit section
    st.subheader(f"Editar Chofer {tipo}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        selected_chofer = st.selectbox(
            f"Seleccionar chofer {tipo}:",
            options=df_filtered['Codigo'].tolist(),
            format_func=lambda x: f"{x} - {df_filtered[df_filtered['Codigo']==x]['Nombre'].iloc[0]}",
            key=f"edit_select_{tipo}"
        )
    
    if selected_chofer:
        chofer_data = df_filtered[df_filtered['Codigo'] == selected_chofer].iloc[0]
        
        with col2:
            new_transporte = st.text_input(
                "Transporte:",
                value=chofer_data['Transporte'] if pd.notna(chofer_data['Transporte']) else "",
                key=f"edit_transporte_{tipo}"
            )
        
        col3, col4 = st.columns([1, 1])
        
        with col3:
            new_nombre = st.text_input(
                "Nombre:",
                value=chofer_data['Nombre'],
                key=f"edit_nombre_{tipo}"
            )
            new_dni = st.text_input(
                "DNI:",
                value=chofer_data['DNI'],
                key=f"edit_dni_{tipo}"
            )
            new_patente = st.text_input(
                "Patente:",
                value=chofer_data['Patente'] if pd.notna(chofer_data['Patente']) else "",
                key=f"edit_patente_{tipo}"
            )
        
        with col4:
            new_semi = st.text_input(
                "Semi:",
                value=chofer_data['Semi'] if pd.notna(chofer_data['Semi']) else "",
                key=f"edit_semi_{tipo}"
            )
            # Extract phone number from WhatsApp link for editing
            current_whatsapp = chofer_data['Whatsapp']
            phone_from_link = ""
            if current_whatsapp and current_whatsapp.startswith('http://wa.me/549'):
                phone_from_link = current_whatsapp.replace('http://wa.me/549', '')
            
            new_whatsapp_num = st.text_input(
                "WhatsApp (solo números):",
                value=phone_from_link,
                key=f"edit_whatsapp_{tipo}"
            )
            new_valor = st.number_input(
                "Valor:",
                value=float(chofer_data['Valor']) if pd.notna(chofer_data['Valor']) else 0.0,
                key=f"edit_valor_{tipo}"
            )
        
        if st.button(f"Actualizar Chofer {tipo}", key=f"update_btn_{tipo}"):
            try:
                whatsapp_link = format_whatsapp_link(new_whatsapp_num)
                
                update_data_by_index(
                    "choferes",
                    chofer_data['id'],
                    {
                        'Nombre': new_nombre,
                        'DNI': new_dni,
                        'Patente': new_patente,
                        'Semi': new_semi,
                        'Whatsapp': whatsapp_link,
                        'Transporte': new_transporte,
                        'Valor': new_valor
                    }
                )
                st.success(f"Chofer {selected_chofer} actualizado correctamente")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar chofer: {e}")

def show_page_choferes():
    st.title("Gestión de Choferes")
    st.markdown("Administración de choferes por tipo: Andresito, Fletero y Transportes")
    
    # Fetch data
    choferes_data = fetch_data_choferes()
    
    if choferes_data.empty:
        st.warning("No hay datos de choferes disponibles")
        choferes_data = pd.DataFrame(columns=['id', 'Codigo', 'Tipo', 'Nombre', 'Patente', 'Semi', 'Whatsapp', 'DNI', 'Transporte', 'Valor'])
    
    # Add new chofer section
    st.subheader("Agregar Nuevo Chofer")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        new_tipo = st.selectbox(
            "Tipo de Chofer:",
            options=['Andresito', 'Fletero', 'Transportes'],
            key="new_tipo"
        )
        new_nombre = st.text_input("Nombre:", key="new_nombre")
        new_dni = st.text_input("DNI:", key="new_dni")
    
    with col2:
        new_patente = st.text_input("Patente:", key="new_patente")
        new_semi = st.text_input("Semi:", key="new_semi")
        new_whatsapp = st.text_input("WhatsApp (solo números):", key="new_whatsapp")
    
    with col3:
        new_transporte = st.text_input("Transporte:", key="new_transporte")
        new_valor = st.number_input("Valor:", value=0.0, key="new_valor")
    
    if st.button("Agregar Chofer", key="add_chofer_btn"):
        if new_nombre and new_dni:
            try:
                # Generate new code
                existing_codes = choferes_data['Codigo'].tolist() if not choferes_data.empty else []
                new_codigo = generate_chofer_code(new_tipo, existing_codes)
                
                # Format WhatsApp link
                whatsapp_link = format_whatsapp_link(new_whatsapp) if new_whatsapp else None
                
                # Insert new chofer
                insert_data("choferes", {
                    'Codigo': new_codigo,
                    'Tipo': new_tipo,
                    'Nombre': new_nombre,
                    'DNI': new_dni,
                    'Patente': new_patente,
                    'Semi': new_semi,
                    'Whatsapp': whatsapp_link,
                    'Transporte': new_transporte,
                    'Valor': new_valor
                })
                
                st.success(f"Chofer {new_codigo} - {new_nombre} agregado correctamente")
                st.cache_data.clear()
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error al agregar chofer: {e}")
        else:
            st.error("Nombre y DNI son campos obligatorios")
    
    st.markdown("---")
    
    # Display tables by type
    tipos = ['Andresito', 'Fletero', 'Transportes']
    
    for tipo in tipos:
        st.subheader(f"Choferes {tipo}")
        df_tipo = choferes_data[choferes_data['Tipo'] == tipo] if not choferes_data.empty else pd.DataFrame()
        
        show_chofer_table(df_tipo, tipo)
        st.markdown("---")

def show_page_trafico_andresito():
    pass



