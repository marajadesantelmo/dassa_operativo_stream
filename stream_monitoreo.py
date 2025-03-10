import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

# Page configurations
st.set_page_config(page_title="Monitoreo", 
                   page_icon="📊", 
                   layout="wide")

# Estilo
with open("styles_mobile.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load data
kpi_df = pd.read_csv('data/monitoreo/kpi.csv')
ventas_por_vendedor_df = pd.read_csv('data/monitoreo/ventas_por_vendedor.csv')
ventas_por_cliente_df = pd.read_csv('data/monitoreo/ventas_por_cliente.csv')
saldos_df = pd.read_csv('data/monitoreo/saldos.csv')
ventas_clientes_nuevos = pd.read_csv('data/monitoreo/ventas_clientes_nuevos.csv')
ventas_totales_por_mes_tabla = pd.read_csv('data/monitoreo/ventas_totales_por_mes_tabla.csv')
ventas_totales_por_mes_grafico = pd.read_csv('data/monitoreo/ventas_totales_por_mes_grafico.csv')
existente_df = pd.read_csv('data/monitoreo/existente.csv')
resumen_mensual_ctns_df = pd.read_csv('data/monitoreo/resumen_mensual_ctns.csv')
kpi_data_expo= pd.read_csv('data/monitoreo/kpi_data_expo.csv')
kpi_data_impo= pd.read_csv('data/monitoreo/kpi_data_impo.csv')
resumen_mensual_ctns_impo = pd.read_csv('data/monitoreo/resumen_mensual_ctns_impo.csv')
resumen_mensual_ctns_expo = pd.read_csv('data/monitoreo/resumen_mensual_ctns_expo.csv')
cnts_impo_ing_mensual_desconsolida = pd.read_csv('data/monitoreo/cnts_impo_ing_mensual_desconsolida.csv')

page_selection = option_menu(
        None,  # No menu title
        ["Ventas", "Operativo"],  
        icons=["bar-chart-line", "gear"],   
        menu_icon="cast",  
        default_index=0, 
        orientation="horizontal")

if page_selection == "Ventas":
    st.markdown(
        """
        <div style="display: flex; align-items: center;">
            <img src="https://raw.githubusercontent.com/marajadesantelmo/dassa_operativo_stream/main/logo_mini.png" style="width: 50px; margin-right: 10px;">
            <h1 style="margin: 0;">Ventas</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    col1.metric(label=kpi_df.iloc[0]['Metric'], value=kpi_df.iloc[0]['Value'])
    col2.metric(label=kpi_df.iloc[1]['Metric'], value=kpi_df.iloc[1]['Value'])

    col3, col4 = st.columns(2)
    col3.metric(label=kpi_df.iloc[2]['Metric'], value=kpi_df.iloc[2]['Value'])
    col4.metric(label=kpi_df.iloc[3]['Metric'], value=kpi_df.iloc[3]['Value'])

    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Ventas por Vendedor")
    st.dataframe(ventas_por_vendedor_df, hide_index=True, use_container_width=True)

    st.subheader("Ventas por Cliente")
    st.dataframe(ventas_por_cliente_df, hide_index=True, use_container_width=True)

    st.subheader("Ventas a Clientes Nuevos")
    st.write(f'Total clientes con alta en los últimos 30 días: {kpi_df.iloc[4]['Value']}')
    st.dataframe(ventas_clientes_nuevos, hide_index=True, use_container_width=True)

    st.subheader("Ventas totales por mes")
    st.write('Valores ajustados por IPC')
    st.bar_chart(ventas_totales_por_mes_grafico.set_index('Mes'))
    st.dataframe(ventas_totales_por_mes_tabla, hide_index=True, use_container_width=True)

    st.subheader("Saldos")
    st.dataframe(saldos_df, hide_index=True, use_container_width=True)
    st.write(f'Total saldos: {kpi_df.iloc[5]['Value']}')

    st.markdown("<hr>", unsafe_allow_html=True)

elif page_selection == "Operativo":
    st.markdown(
        """
        <div style="display: flex; align-items: center;">
            <img src="https://raw.githubusercontent.com/marajadesantelmo/dassa_operativo_stream/main/logo_mini.png" style="width: 50px; margin-right: 10px;">
            <h1 style="margin: 0;">Operativo</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.header("CTNs IMPO ingresados")
    st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Mes actual</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Mes anterior</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Prom. mensual</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Proy. mes actual</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Vol. Ingresado</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Vol. Egresado</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Desco. mes actual</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Desco. %</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
        </div>
        """.format(
            int(kpi_data_impo.iloc[0]['Mes actual']),
            int(kpi_data_impo.iloc[0]['Mes anterior']),
            int(kpi_data_impo.iloc[0]['Promedio mensual']),
            int(kpi_data_impo.iloc[0]['Proyeccion mes actual']),
            int(kpi_data_impo.iloc[0]['Vol. Ingresado']),
            int(kpi_data_impo.iloc[0]['Vol. Egresado']),
            int(kpi_data_impo.iloc[0]['Desco. mes actual']),
            kpi_data_impo.iloc[0]['Desco. %']
        ),
        unsafe_allow_html=True
    )
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("CTNs EXPO egresados")
    st.markdown("""
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Mes actual</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Mes anterior</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Prom. mensual</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Proy. mes actual</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Vol. Ingresado</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
            <div style="display: flex; flex-direction: column; align-items: center;">
                <h6>Vol. Egresado</h6>
                <p style="font-size: calc(0.8em + 0.8vw);">{}</p>
            </div>
        </div>
        """.format(
            int(kpi_data_expo.iloc[0]['Mes actual']),
            int(kpi_data_expo.iloc[0]['Mes anterior']),
            int(kpi_data_expo.iloc[0]['Promedio mensual']),
            int(kpi_data_expo.iloc[0]['Proyeccion mes actual']),
            int(kpi_data_expo.iloc[0]['Vol. Ingresado']),
            int(kpi_data_expo.iloc[0]['Vol. Egresado'])
        ),
        unsafe_allow_html=True
    )

    st.subheader("Evolución mensual de CTNs")
    st.line_chart(resumen_mensual_ctns_df.set_index('Mes'))

    st.subheader("Comparativa mensual contenedores")
    st.write('CNTS IMPO')
    st.dataframe(resumen_mensual_ctns_impo, hide_index=True, use_container_width=True)

    st.write('CNTS EXPO')
    st.dataframe(resumen_mensual_ctns_expo, hide_index=True, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Historico IMPO T/TD")
    st.dataframe(cnts_impo_ing_mensual_desconsolida, hide_index=True, use_container_width=True)
