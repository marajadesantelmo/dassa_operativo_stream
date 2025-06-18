import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, insert_table_data

st.set_page_config(page_title="Preingreso Playón DASSA", page_icon="🚛", layout="centered")

def generate_queue_number():
    preingreso_data = fetch_table_data("preingreso")
    return preingreso_data.shape[0] + 1

def submit_form(data):
    queue_number = generate_queue_number()
    data["numero_fila"] = queue_number
    insert_table_data("preingreso", [data])
    return queue_number

st.title("Formulario de Preingreso - Playón DASSA")
st.image('logo.png')
st.markdown("Complete los siguientes campos para registrar su arribo al playón.")

with st.form("preingreso_form"):
    cliente_mercaderia = st.text_input("Cliente / Mercadería", max_chars=100)
    nombre_chofer = st.text_input("Nombre del chofer", max_chars=100)
    dni_chofer = st.text_input("DNI del chofer", max_chars=20)
    patente_camion = st.text_input("Patente del camión", max_chars=20)
    patente_acoplado = st.text_input("Patente del acoplado", max_chars=20)
    celular_whatsapp = st.text_input("Número de celular o WhatsApp", max_chars=20)
    remito_permiso_embarque = st.text_input("Número de Remito o Permiso de Embarque", max_chars=50)
    tipo_carga = st.text_input("Observaciones / Tipo de carga / Lote / Partida", max_chars=50)

    submitted = st.form_submit_button("Registrar")
    if submitted:
        if all([cliente_mercaderia, nombre_chofer, dni_chofer, patente_camion, patente_acoplado, celular_whatsapp, remito_permiso_embarque]):
            data = {
                "cliente_mercaderia": cliente_mercaderia,
                "nombre_chofer": nombre_chofer,
                "dni_chofer": dni_chofer,
                "patente_camion": patente_camion,
                "patente_acoplado": patente_acoplado,
                "celular_whatsapp": celular_whatsapp,
                "remito_permiso_embarque": remito_permiso_embarque,
                "tipo_carga": tipo_carga
            }
            queue_number = submit_form(data)
            st.success(f"✅ Registro exitoso. Usted es el camión N° {queue_number} en la fila del día.")
            st.info("Lo contactaremos al número de Whatsapp ingresado.")
            st.info("Una vez autorizado el ingreso tiene 15 minutos de tolerancia para ingresar.")
            st.image("indicaciones.jpg")
        else:
            st.error("Por favor, complete todos los campos obligatorios.")
