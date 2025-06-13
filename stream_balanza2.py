import streamlit as st
import pandas as pd
from datetime import datetime
from supabase_connection import fetch_table_data
from utils import highlight, generar_comprobante

def fetch_data_balanza():
    balanza = pd.read_csv('data/balanza.csv') # Me quedo con la info de balanza completa para generar comprobante
    balanza['DNI'] = balanza['DNI'].fillna('-').astype(str).str.replace('.0', '', regex=False)
    balanza = balanza.fillna("-")
    balanza_impo = balanza[balanza['tipo_oper'] == 'Importacion']
    balanza_expo = balanza[balanza['tipo_oper'] == 'Exportacion']
    columns_impo = ['ID Pesada', 'Cliente', 'ATA', 'Contenedor', 'Entrada', 'Salida', 'Peso Bruto', 'Peso Tara',
       'Peso Neto', 'Tara CNT', 'Peso Mercadería', 'Descripción', 'Patente Chasis', 'Patente Semi', 'Chofer', 'DNI',
       'Booking', 'Precinto', 'Tipo Doc', 'Estado']
    columns_expo = ['ID Pesada', 'Cliente', 'ATA',  'Entrada', 'Salida', 'Peso Bruto', 'Peso Tara',
       'Peso Neto', 'Peso Mercadería', 'Descripción', 'Patente Chasis', 'Patente Semi', 'Chofer', 'DNI', 'Observaciones',
       'Booking', 'Permiso Emb.', 'Tipo Doc', 'Estado']
    balanza_impo = balanza_impo[columns_impo]
    balanza_expo = balanza_expo[columns_expo]
    balanza_impo = balanza_impo.sort_values(by='Estado', ascending=True)
    balanza_expo = balanza_expo.sort_values(by='Estado', ascending=True)
    balanza_historico = pd.read_csv('data/historico_balanza.csv')
    balanza_historico['DNI'] = balanza_historico['DNI'].fillna('-').astype(str).str.replace('.0', '', regex=False)
    balanza_historico = balanza_historico.fillna("-")
    balanza_historico_impo = balanza_historico[balanza_historico['tipo_oper'] == 'Importacion']
    balanza_historico_expo = balanza_historico[balanza_historico['tipo_oper'] == 'Exportacion']
    columns_impo_historico = ['ID Pesada', 'Fecha', 'Cliente', 'ATA', 'Contenedor', 'Entrada', 'Salida', 'Peso Bruto', 'Peso Tara',
       'Peso Neto', 'Tara CNT', 'Peso Mercadería', 'Descripción', 'Patente Chasis', 'Patente Semi', 'Chofer', 'DNI',
       'Booking', 'Precinto', 'Tipo Doc', 'Estado']
    columns_expo_historico = ['ID Pesada', 'Fecha', 'Cliente', 'ATA',  'Entrada', 'Salida', 'Peso Bruto', 'Peso Tara',
       'Peso Neto', 'Peso Mercadería', 'Descripción', 'Patente Chasis', 'Patente Semi', 'Chofer', 'DNI', 'Observaciones',
       'Booking', 'Permiso Emb.', 'Tipo Doc', 'Estado']
    balanza_historico_impo = balanza_historico_impo[columns_impo_historico]
    balanza_historico_expo = balanza_historico_expo[columns_expo_historico]
    balanza_historico_impo = balanza_historico_impo.sort_values(by='Estado', ascending=True)
    balanza_historico_expo = balanza_historico_expo.sort_values(by='Estado', ascending=True)
    
    return balanza, balanza_impo, balanza_expo, balanza_historico_impo, balanza_historico_expo, balanza_historico


def fetch_last_update():
    with open('data/ultima_actualizacion.csv', 'r', encoding='utf-8') as f:
        last_update = f.read().strip()
    return last_update

@st.cache_data(ttl=60)
def fetch_last_update():
    update_log = fetch_table_data("update_log")
    if not update_log.empty:
        try:
            last_update = update_log[update_log['table_name'] == 'Balanza']['last_update'].max()
            return pd.to_datetime(last_update).strftime("%d/%m/%Y %H:%M")
        except Exception as e:
            st.error(f"Error al obtener la última actualización: {e}")
            return "No disponible"
    return "No disponible"

def show_page_balanza():
    # Load data
    balanza, balanza_impo, balanza_expo, balanza_historico_impo, balanza_historico_expo, balanza_historico = fetch_data_balanza()
    last_update = fetch_last_update()

    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
        st.info(f'Última actualización: {last_update}')
    with col_title:
        current_day = datetime.now().strftime("%d/%m/%Y")
        st.title(f"Operaciones en balanza del {current_day}")
    st.subheader("Importación")
    columns_to_format = ['ID Pesada', 'Peso Bruto', 'Peso Neto', 'Tara CNT', 'Peso Mercadería']

    st.dataframe(balanza_impo.style.apply(highlight, axis=1), column_config={col: st.column_config.NumberColumn(col, format="%s") for col in columns_to_format}, hide_index=True, use_container_width=True)
    st.subheader("Exportación")
    st.dataframe(balanza_expo.style.apply(highlight, axis=1), column_config={col: st.column_config.NumberColumn(col, format="%s") for col in columns_to_format}, hide_index=True, use_container_width=True)

    st.subheader("Generar Comprobante")
    id_pesada = st.selectbox("Seleccione el ID de Pesada", balanza['ID Pesada'].tolist())
    if st.button("Generar Comprobante"):
        balanza_row = balanza[balanza['ID Pesada'] == id_pesada].iloc[0]
        pdf = generar_comprobante(balanza_row)
        pdf_output = f"comprobante_pesada_{id_pesada}.pdf"
        pdf.output(pdf_output)
        with open(pdf_output, "rb") as file:
            st.download_button(
                label="Descargar Comprobante",
                data=file,
                file_name=pdf_output,
                mime="application/pdf"
            )
        st.success(f"Comprobante generado: {pdf_output}")
    # Load data

    
    st.title("Histórico de Pesadas")
    st.write("Importación")
    
    # Add date, ID Pesada, and Cliente filters
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        start_date_historico = pd.to_datetime(st.date_input("Fecha Inicio", value=pd.to_datetime(balanza_historico_impo['Fecha'], format='%d/%m/%Y').min(), key='start_date_historico'))
    with col2:
        end_date_historico = pd.to_datetime(st.date_input("Fecha Fin", value=pd.to_datetime(balanza_historico_impo['Fecha'], format='%d/%m/%Y').max(), key='end_date_historico'))
    with col3:
        id_pesada_filter = st.selectbox("ID Pesada", options=["Todos"] + sorted(balanza_historico_impo['ID Pesada'].unique().tolist()), key='id_pesada_filter')
    with col4:
        # Ensure Cliente column is treated as strings
        cliente_options = ["Todos"] + sorted(balanza_historico_impo['Cliente'].astype(str).unique().tolist())
        cliente_filter = st.selectbox("Cliente", options=cliente_options, key='cliente_filter')

    # Filter data based on the selected criteria
    filtered_historico_impo = balanza_historico_impo[
        (pd.to_datetime(balanza_historico_impo['Fecha'], format='%d/%m/%Y') >= start_date_historico) &
        (pd.to_datetime(balanza_historico_impo['Fecha'], format='%d/%m/%Y') <= end_date_historico)
    ]
    if id_pesada_filter != "Todos":
        filtered_historico_impo = filtered_historico_impo[filtered_historico_impo['ID Pesada'] == id_pesada_filter]
    if cliente_filter != "Todos":
        filtered_historico_impo = filtered_historico_impo[filtered_historico_impo['Cliente'].astype(str) == cliente_filter]

    st.dataframe(filtered_historico_impo, column_config={col: st.column_config.NumberColumn(col, format="%s") for col in columns_to_format}, hide_index=True, use_container_width=True)

    st.write("Exportación")
    
    # Repeat the same filtering logic for export data
    filtered_historico_expo = balanza_historico_expo[
        (pd.to_datetime(balanza_historico_expo['Fecha'], format='%d/%m/%Y') >= start_date_historico) &
        (pd.to_datetime(balanza_historico_expo['Fecha'], format='%d/%m/%Y') <= end_date_historico)
    ]
    if id_pesada_filter != "Todos":
        filtered_historico_expo = filtered_historico_expo[filtered_historico_expo['ID Pesada'] == id_pesada_filter]
    if cliente_filter != "Todos":
        filtered_historico_expo = filtered_historico_expo[filtered_historico_expo['Cliente'].astype(str) == cliente_filter]

    st.dataframe(filtered_historico_expo, column_config={col: st.column_config.NumberColumn(col, format="%s") for col in columns_to_format}, hide_index=True, use_container_width=True)

    st.subheader("Generar Comprobante")
    id_pesada_historico = st.selectbox("Seleccione el ID de Pesada Histórico", balanza_historico_impo['ID Pesada'].tolist())
    if st.button("Generar Comprobante Histórico"):
        balanza_row_historico = balanza_historico[balanza_historico['ID Pesada'] == id_pesada_historico].iloc[0] 
        pdf_historico = generar_comprobante(balanza_row_historico)
        pdf_output_historico = f"comprobante_pesada_historico_{id_pesada_historico}.pdf"
        pdf_historico.output(pdf_output_historico)
        with open(pdf_output_historico, "rb") as file:
            st.download_button(
                label="Descargar Comprobante Histórico",
                data=file,
                file_name=pdf_output_historico,
                mime="application/pdf"
            )
        st.success(f"Comprobante histórico generado: {pdf_output_historico}")

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_balanza()
        time.sleep(60)  
        st.experimental_rerun()

