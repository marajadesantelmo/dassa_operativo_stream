import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight, generar_comprobante

@st.cache_data(ttl=60) 
def fetch_data_balanza():
    balanza = pd.read_csv('data/balanza.csv') # Me quedo con la info de balanza completa para generar comprobante
    balanza_impo = balanza[balanza['tipo_oper'] == 'Importacion']
    balanza_expo = balanza[balanza['tipo_oper'] == 'Exportacion']
    columns_impo = ['ID Pesada', 'Cliente', 'ATA', 'Contenedor', 'Entrada', 'Salida', 'Peso Bruto', 'Peso Tara',
       'Peso Neto', 'Tara CNT', 'Peso Mercadería', 'Descripción', 'Patente Chasis', 'Patente Semi', 'Chofer', 
       'Booking', 'Precinto', 'Estado']
    columns_expo = ['ID Pesada', 'Cliente', 'ATA',  'Entrada', 'Salida', 'Peso Bruto', 'Peso Tara',
       'Peso Neto', 'Peso Mercadería', 'Descripción', 'Patente Chasis', 'Patente Semi', 'Chofer', 'Observaciones',
       'Booking', 'Permiso Emb.', 'Estado']
    balanza_impo = balanza_impo[columns_impo]
    balanza_expo = balanza_expo[columns_expo]
    balanza_impo = balanza_impo.sort_values(by='Estado', ascending=True)
    balanza_expo = balanza_expo.sort_values(by='Estado', ascending=True)
    return balanza, balanza_impo, balanza_expo

def show_page_balanza():
    # Load data
    balanza, balanza_impo, balanza_expo = fetch_data_balanza()

    col_logo, col_title = st.columns([2, 5])
    with col_logo:
        st.image('logo.png')
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

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_balanza()
        time.sleep(60)  
        st.experimental_rerun()

