import streamlit as st
import pandas as pd
import time
from datetime import datetime
from utils import highlight
import matplotlib.pyplot as plt 
from matplotlib.figure import Figure

@st.cache_data(ttl=60) 
def fetch_data_plazoleta():
    arribos = pd.read_csv('data/arribos.csv')
    arribos_semana = pd.read_csv('data/arribos_semana.csv')
    arribos_semana_pendientes = arribos_semana[arribos_semana['arribado'] == 0]
    tabla_arribos_pendientes = arribos_semana_pendientes
    arribos_por_fecha = tabla_arribos_pendientes['fecha'].value_counts().reset_index()
    arribos_por_fecha.columns = ['Fecha', 'CNTs']
    tabla_arribos_pendientes = tabla_arribos_pendientes[['fecha', 'contenedor', 'cliente', 'T-TD']]
    tabla_arribos_pendientes.columns = ['Fecha', 'Contenedor', 'Cliente', 'T-TD']
    pendiente_desconsolidar = pd.read_csv('data/pendiente_desconsolidar.csv')
    existente_plz = pd.read_csv('data/existente_plz.csv')
    existente_plz = existente_plz[existente_plz['Operacion'].str.contains("-0-")] #Saco la mercaderia que esta en PLZ (solo quiero tachos)
    existente_plz_clientes = existente_plz['Cliente'].value_counts().reset_index()
    existente_plz_clientes.columns = ['Cliente', 'CTNs']
    cont_nac = pd.read_csv('data/contenedores_nacionales.csv')
    cont_nac_clientes = cont_nac['CLIENTE'].value_counts().reset_index()
    cont_nac_clientes.columns = ['Cliente', 'CTNs']
    arribos_expo_ctns = pd.read_csv('data/arribos_expo_ctns.csv')
    arribos_expo_ctns = arribos_expo_ctns[~arribos_expo_ctns['Estado'].str.contains('Arribado', na=False)]
    arribos_expo_ctns = arribos_expo_ctns[['Fecha', 'Contenedor', 'Cliente']]
    listos_para_remitir = pd.read_csv('data/listos_para_remitir.csv')
    vacios_disponibles = pd.read_csv('data/vacios_disponibles.csv')
    existente_plz_expo = pd.concat([listos_para_remitir[['Cliente', 'Contenedor']], vacios_disponibles[['Cliente', 'Contenedor']]])
    existente_plz_expo_clientes = existente_plz_expo['Cliente'].value_counts().reset_index()
    existente_plz_expo_clientes.columns = ['Cliente', 'CTNs']

    ctns_impo_plz = existente_plz.shape[0]
    ctns_expo_plz = listos_para_remitir.shape[0] + vacios_disponibles.shape[0]
    ctns_nac = cont_nac.shape[0]
    disponibles = 220 - ctns_impo_plz - ctns_expo_plz - ctns_nac
    tabla_resumen = pd.DataFrame({
        'Contenedor': ['Importación', 'Exportación', 'Nacional', 'Disponibles'],
        'Cantidad': [ctns_impo_plz, ctns_expo_plz, ctns_nac, disponibles]
    })
    tabla_resumen['%'] = (tabla_resumen['Cantidad'] / 220) * 100
    tabla_resumen['%'] = tabla_resumen['%'].round(0).astype(str) + '%'

    return (arribos, pendiente_desconsolidar, existente_plz, existente_plz_clientes, cont_nac, cont_nac_clientes, arribos_semana, 
            arribos_semana_pendientes, tabla_arribos_pendientes, arribos_por_fecha, arribos_expo_ctns, 
            listos_para_remitir, vacios_disponibles, existente_plz_expo_clientes, tabla_resumen)

def show_page_plazoleta():
    # Load data
    (arribos, pendiente_desconsolidar, existente_plz, existente_plz_clientes, cont_nac, cont_nac_clientes, arribos_semana,  
    arribos_semana_pendientes, tabla_arribos_pendientes, arribos_por_fecha, arribos_expo_ctns, 
    listos_para_remitir, vacios_disponibles, existente_plz_expo_clientes, tabla_resumen) = fetch_data_plazoleta()

    col_logo, col_title, col_pie_chart, col_tabla = st.columns([1, 2, 1, 2])
    with col_logo:
        st.image('logo.png')
    with col_title:
        st.markdown("<h1 style='text-align: center;'>Estado actual de la Plazoleta</h1>", unsafe_allow_html=True)
    with col_pie_chart:
        pie_chart = st.empty()
        fig = Figure(figsize=(4, 4))
        ax = fig.add_subplot(111)
        tabla_resumen.set_index('Contenedor')['Cantidad'].plot.pie(
            autopct=lambda p: f'{p:.0f}%' if p > 0 else '',
            ylabel='',
            textprops={'fontsize': 12, 'color': 'black'},  # Double font size and set percentage labels to black
            colors=plt.cm.Paired.colors,
            ax=ax
        )
        for text in ax.texts:
            if text.get_text().endswith('%'):  # Check if it's a percentage label
                text.set_color('black')  # Keep percentage labels black
            else:
                text.set_color('white')  # Set category labels to white
        fig.patch.set_alpha(0)  # Set transparent background
        ax.set_title('')  # Remove title
        pie_chart.pyplot(fig)
    with col_tabla:
        st.dataframe(tabla_resumen, hide_index=True, use_container_width=True)

    col_arribos, col_existente = st.columns(2)

    with col_arribos:
        st.header('Arribos')
        st.markdown("""
        <div style="display: flex; justify-content: space-between; width: 100%;">
            <div style="text-align: center; flex: 1;">
            <h6>Ptes. IMPO</h6>
            <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
            </div>
            <div style="text-align: center; flex: 1;">
            <h6>House</h6>
            <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
            </div>
            <div style="text-align: center; flex: 1;">
            <h6>TD</h6>
            <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
            </div>
        </div>
        """.format(
            int(arribos_semana_pendientes.shape[0]),
            int(arribos_semana_pendientes[arribos_semana_pendientes['T-TD'] == 'T'].shape[0]),
            int(arribos_semana_pendientes[arribos_semana_pendientes['T-TD'] == 'TD'].shape[0]),
        ),
        unsafe_allow_html=True
        )
        st.write("Arribos pendientes IMPO")
        st.dataframe(tabla_arribos_pendientes, hide_index=True, use_container_width=True)
        st.metric(label="Ptes. EXPO", value=arribos_expo_ctns.shape[0])
        st.write("Arribos pendientes EXPO")
        st.dataframe(arribos_expo_ctns, hide_index=True, use_container_width=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    with col_existente:
        st.header("Existente en Plazoleta")
        st.markdown("""
        <div style="display: flex; justify-content: space-between; width: 100%;">
            <div style="text-align: center; flex: 1;">
            <h6>Total IMPO</h6>
            <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
            </div>
            <div style="text-align: center; flex: 1;">
            <h6>House</h6>
            <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
            </div>
            <div style="text-align: center; flex: 1;">
            <h6>TD</h6>
            <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
            </div>
        </div>
        """.format(
            int(existente_plz.shape[0]),
            int(existente_plz[existente_plz['T-TD'] != 'TD'].shape[0]),
            int(existente_plz[existente_plz['T-TD'] == 'TD'].shape[0]),
        ),
        unsafe_allow_html=True
        )
        st.write("Resumen por cliente")
        st.dataframe(existente_plz_clientes, hide_index=True, use_container_width=True)
        st.markdown("""
        <div style="display: flex; justify-content: space-between; width: 100%;">
            <div style="text-align: center; flex: 1;">
            <h6>Total EXPO</h6>
            <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
            </div>
            <div style="text-align: center; flex: 1;">
            <h6>Consolidado</h6>
            <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
            </div>
            <div style="text-align: center; flex: 1;">
            <h6>Vacios</h6>
            <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
            </div>
        </div>
        """.format(
            int(listos_para_remitir.shape[0] + vacios_disponibles.shape[0]),
            int(listos_para_remitir.shape[0]),
            int(vacios_disponibles.shape[0]),
        ),
        unsafe_allow_html=True
        )
        st.write("Resumen por cliente")
        st.dataframe(existente_plz_expo_clientes, hide_index=True, use_container_width=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Contenedores Nacional")
        # First row of metrics
    st.markdown("""
    <div style="display: flex; justify-content: space-between; width: 100%;">
        <div style="text-align: center; flex: 1;">
        <h6>Existente</h6>
        <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
        </div>
        <div style="text-align: center; flex: 1;">
        <h6>Cargados</h6>
        <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
        </div>
        <div style="text-align: center; flex: 1;">
        <h6>Vacios</h6>
        <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
        </div>
    </div>
    """.format(
        int(cont_nac['Contenedor'].nunique()),
        int(cont_nac[cont_nac['CARGADO'].str.contains(r'\b(?:SI|si|Si)\b', regex=True, na=False)].shape[0]),
        int(cont_nac[cont_nac['CARGADO'].str.contains(r'\b(?:NO|no|No)\b', regex=True, na=False)].shape[0])
    ),
    unsafe_allow_html=True
    )
    
    # Second row of metrics
    st.markdown("""
    <div style="display: flex; justify-content: space-between; width: 100%;">
        <div style="text-align: center; flex: 1;">
        <h6>Rollos</h6>
        <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
        </div>
        <div style="text-align: center; flex: 1;">
        <h6>Cueros cargados</h6>
        <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
        </div>
        <div style="text-align: center; flex: 1;">
        <h6>Cueros disponibles</h6>
        <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
        </div>
        <div style="text-align: center; flex: 1;">
        <h6>Otros</h6>
        <p style="font-size: calc(1.2em + 1vw); font-weight: bold; margin: 0;">{}</p>
        </div>
    </div>
    """.format(
        int(cont_nac[cont_nac['OBSERVACION'].str.contains(r'\b(?:ROLLOS|Rollo)\b', regex=True, na=False)].shape[0]),
        int(cont_nac[
            cont_nac['OBSERVACION'].str.contains(r'\b(?:CUERO|Cuero)\b', regex=True, na=False) &
            cont_nac['CARGADO'].str.contains(r'\b(?:SI|si|Si)\b', regex=True, na=False)
        ].shape[0]),
        int(cont_nac[
            cont_nac['OBSERVACION'].str.contains(r'\b(?:CUERO|Cuero)\b', regex=True, na=False) &
            cont_nac['CARGADO'].str.contains(r'\b(?:NO|no|No)\b', regex=True, na=False)
        ].shape[0]),
        int(cont_nac[
            (~cont_nac['OBSERVACION'].str.contains(r'\b(?:ROLLOS|Rollo|CUERO|Cuero)\b', regex=True, na=False)) &
            (cont_nac['CARGADO'].str.contains(r'\b(?:SI|si|Si)\b', regex=True, na=False))
        ].shape[0])
    ),
    unsafe_allow_html=True
    )
    
    st.dataframe(cont_nac_clientes, hide_index=True, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)

# Run the show_page function
if __name__ == "__main__":
    while True:
        show_page_plazoleta()
        time.sleep(60)  
        st.experimental_rerun()

