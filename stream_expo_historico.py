import streamlit as st
import pandas as pd
def show_page():
    # Load data
    arribos = pd.read_csv('data/arribos.csv')
    arribos = arribos[['terminal', 'turno', 'contenedor', 'cliente', 'bookings', 'tipo_cnt', 'tiempo_transcurrido', 'Estado']]
    arribos.columns = ['Terminal', 'Turno', 'Contenedor', 'Cliente', 'Bookings', 'Tipo', 'Temp.', 'Estado']

    pendiente_desconsolidar= pd.read_csv('data/pendiente_desconsolidar.csv')
    pendiente_desconsolidar = pendiente_desconsolidar[['contenedor', 'Estado', 'cliente', 'Entrega', 'vto_vacio', 'tipo_cnt', 'peso']]
    pendiente_desconsolidar.columns = ['Contenedor', 'Estado', 'Cliente', 'Entrega', 'Vto. Vacio', 'Tipo', 'Peso']

    turnos= pd.read_csv('data/turnos.csv')

    verificaciones_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (turnos['destino'] == 'Verificacion')]
    verificaciones_impo = verificaciones_impo[['dia', 'cliente', 'desc_merc', 'contenedor', 'Envase', 'cantidad', 'ubicacion']]
    verificaciones_impo.columns = ['Dia', 'Cliente', 'Desc. Merc.', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.']

    retiros = turnos[(turnos['tipo_oper'] == 'Importacion') & (turnos['destino'] == 'Retiro')]
    retiros = retiros[['dia', 'cliente', 'conocim1', 'contenedor', 'Envase', 'cantidad', 'ubicacion', 'Estado']]
    retiros.columns = ['Dia', 'Cliente', 'Conocim.', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.', 'Estado']

    otros_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (~turnos['destino'].isin(['Retiro', 'Verificacion']))]
    otros_impo = otros_impo[['dia', 'hora', 'id', 'cliente', 'contenedor', 'Envase', 'cantidad', 'ubicacion']]
    otros_impo.columns = ['Dia', 'Hora', 'Operacion', 'Cliente', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.']

    remisiones = turnos[turnos['destino'] == 'Remision']
    consolidados = turnos[turnos['destino'] == 'Consolidado']

    st.title("DASSA - Operaciones de EXPO")

    def highlight_arribado(row):
        if "Arribado" in row['Estado']:
            return ['background-color: darkgreen; color: black' for _ in row]
        elif row['Estado'] == "Pendiente ingreso":
            return ['background-color: lightyellow' for _ in row]
        else:
            return ['' for _ in row]

    def highlight_pendiente_desco(row):
        if row['Estado'] == "Vacio":
            return ['background-color: lightcoral' for _ in row]
        else:
            return ['' for _ in row]

    # Create two columns
    col1, col2 = st.columns(2)

    # Column 1: Arribos
    with col1:
        st.header("Arribos Contenedores")
        st.dataframe(arribos.style.apply(highlight_arribado, axis=1), hide_index=True)

    # Column 2: Pendiente Desconsolidar
    with col2:
        st.header("Pendiente Desconsolidar y Vacios")
        st.dataframe(pendiente_desconsolidar.style.apply(highlight_pendiente_desco, axis=1).format(precision=0), hide_index=True)
