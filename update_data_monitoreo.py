import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta
from tokens import username, password
from utils import rellenar_df_vacio
import gspread
from gspread_dataframe import set_with_dataframe

if os.path.exists('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream'):
    os.chdir('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream')
elif os.path.exists('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream'):
    os.chdir('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream')
else:
    print("Se usa working directory por defecto")

path = '//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/'

print('Actualizando información operativa Orden del Día DASSA')
print('Descargando datos de SQL')
server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

fecha = datetime.now().strftime('%Y-%m-%d')
fecha_ant = datetime.now() - timedelta(days=120)
fecha_ant = fecha_ant.strftime('%Y-%m-%d')
fecha_ant_ult3dias = datetime.now() - timedelta(days=3)
fecha_ant_ult3dias = fecha_ant_ult3dias.strftime('%Y-%m-%d')
first_day_prev_month = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
last_day_prev_month = datetime.now().replace(day=1) - timedelta(days=1)

# Querys
cursor.execute("""
SELECT fecha_vto, tp_cpte, aplicacion, adicional, debe, haber
FROM DEPOFIS.DASSA.CtaCcteD
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
saldos_sql= pd.DataFrame.from_records(rows, columns=columns)

cursor.execute(f"""
SELECT Factura, tipo, fecha_emi, fecha_vto, [Neto Gravado], [Neto No Gravado], [Importe Total], [Razon Social], vendedor
FROM DEPOFIS.DASSA.Facturacion
WHERE fecha_emi > '2024-01-01'
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
facturacion_sql = pd.DataFrame.from_records(rows, columns=columns)

# Procesamientos dataframes

# Formateo de facturacion
def transformar_facturacion(df): 
    df['fecha_emi'] = pd.to_datetime(df['fecha_emi'])
    df = df[df['fecha_emi'] > pd.to_datetime(fecha_ant)].copy()
    df['Neto'] = df['Neto Gravado'] + df['Neto No Gravado']
    df.loc[df['tipo'] == 3, 'Factura'] = 'NdC ' + df['Factura'].astype(str)
    df = df.drop(columns=['tipo'])
    df = df.groupby(
        ['Factura', 'fecha_emi', 'fecha_vto', 'Razon Social']).agg({
        'Neto': 'sum',
        'Importe Total': 'sum', 
        'vendedor': 'first'}).reset_index()
    df['Razon Social'] = df['Razon Social'].str.strip().str.title()
    df.rename(columns={'fecha_emi': 'Emision', 'fecha_vto': 'Vencimiento', 'vendedor': 'cod_vendedor'}, inplace=True)
    return df

facturacion = transformar_facturacion(facturacion_sql)
diccionario_vendedores = pd.read_excel(path + 'diccionario_vendedores_puros_dassa.xlsx')
facturacion = facturacion.merge(diccionario_vendedores, on='cod_vendedor', how='left')

def transformar_saldos(df): 
    df['saldo'] = df['debe'] - df['haber']
    df = df.groupby(['adicional']).agg({'saldo': 'sum'}).reset_index()
    df = df[df['saldo'] > 1]
    df['adicional'] = df['adicional'].str.strip().str.title()
    df.rename(columns={'adicional': 'Cliente', 
                       'saldo': 'Saldo'}, 
                       inplace=True)
    df = df[['Cliente',  'Saldo']]
    df['Saldo'] = df['Saldo'].round(0)
    df['Saldo'] = df['Saldo'].apply(lambda x: f"${x:,.0f}".replace(",", "."))
    return df

saldos = transformar_saldos(saldos_sql)

# Calculate sales KPIs
current_month = datetime.now().replace(day=1)
previous_month = (current_month - timedelta(days=1)).replace(day=1)
same_period_last_month = (current_month - timedelta(days=30)).replace(day=1)
last_12_months = (current_month - timedelta(days=365)).replace(day=1)

# Filter data for KPIs
current_month_sales = facturacion[(facturacion['Emision'] >= current_month.strftime('%Y-%m-%d'))]
previous_month_sales = facturacion[(facturacion['Emision'] >= previous_month.strftime('%Y-%m-%d')) & (facturacion['Emision'] < current_month.strftime('%Y-%m-%d'))]
same_period_last_month_sales = facturacion[(facturacion['Emision'] >= same_period_last_month.strftime('%Y-%m-%d')) & (facturacion['Emision'] < (same_period_last_month + timedelta(days=30)).strftime('%Y-%m-%d'))]
last_12_months_sales = facturacion[(facturacion['Emision'] >= last_12_months.strftime('%Y-%m-%d'))]

# Calculate totals
current_month_total = round(current_month_sales['Importe Total'].sum(), 0)
previous_month_total = round(previous_month_sales['Importe Total'].sum(), 0)
same_period_last_month_total = round(same_period_last_month_sales['Importe Total'].sum(), 0)
monthly_average_last_12_months = round(last_12_months_sales['Importe Total'].sum() / 12, 0)

# Create KPIs dataframe
kpis = pd.DataFrame({
    'Metric': ['Mes actual', 'Mes anterior', 'Mismo periodo mes anterior', 'Promedio mensual ultimos 12 meses'],
    'Value': [current_month_total, previous_month_total, same_period_last_month_total, monthly_average_last_12_months]
})

kpis['Value'] = kpis['Value'].apply(lambda x: f"${x:,.0f}".replace(",", "."))

print(kpis)

# Ventas por cliente
ventas_por_cliente_mes_actual = current_month_sales.groupby('Razon Social').agg({'Importe Total': 'sum'}).reset_index()
ventas_por_cliente_mes_anterior = previous_month_sales.groupby('Razon Social').agg({'Importe Total': 'sum'}).reset_index()
ventas_por_cliente = ventas_por_cliente_mes_actual.merge(ventas_por_cliente_mes_anterior, on='Razon Social', how='outer', suffixes=('_actual', '_anterior'))
ventas_por_cliente = ventas_por_cliente.fillna(0)
ventas_por_cliente['Importe Total_actual'] = ventas_por_cliente['Importe Total_actual'].round(0)
ventas_por_cliente['Importe Total_anterior'] = ventas_por_cliente['Importe Total_anterior'].round(0)
ventas_por_cliente.rename(columns={'Razon Social': 'Cliente', 
                       'Importe Total_actual': 'Mes actual', 
                       'Importe Total_anterior': 'Mes anterior'}, inplace=True)
ventas_por_cliente = ventas_por_cliente.sort_values(by='Mes actual', ascending=False)
ventas_por_cliente['Mes actual'] = ventas_por_cliente['Mes actual'].apply(lambda x: f"${x:,.0f}")
ventas_por_cliente['Mes anterior'] = ventas_por_cliente['Mes anterior'].apply(lambda x: f"${x:,.0f}")
print(ventas_por_cliente)

# Ventas por vendedor
ventas_por_vendedor_mes_actual = current_month_sales.groupby('Vendedor').agg({'Importe Total': 'sum'}).reset_index()
ventas_por_vendedor_mes_anterior = previous_month_sales.groupby('Vendedor').agg({'Importe Total': 'sum'}).reset_index()
ventas_por_vendedor = ventas_por_vendedor_mes_actual.merge(ventas_por_vendedor_mes_anterior, on='Vendedor', how='outer', suffixes=('_actual', '_anterior'))
ventas_por_vendedor = ventas_por_vendedor.fillna(0)
ventas_por_vendedor['Importe Total_actual'] = ventas_por_vendedor['Importe Total_actual'].round(0)
ventas_por_vendedor['Importe Total_anterior'] = ventas_por_vendedor['Importe Total_anterior'].round(0)
ventas_por_vendedor.rename(columns={'Vendedor': 'Vendedor', 
                       'Importe Total_actual': 'Mes actual', 
                       'Importe Total_anterior': 'Mes anterior'}, inplace=True)
ventas_por_vendedor = ventas_por_vendedor.sort_values(by='Mes actual', ascending=False)
ventas_por_vendedor['Mes actual'] = ventas_por_vendedor['Mes actual'].apply(lambda x: f"${x:,.0f}")
ventas_por_vendedor['Mes anterior'] = ventas_por_vendedor['Mes anterior'].apply(lambda x: f"${x:,.0f}")
print(ventas_por_vendedor)




kpis.to_csv('data/monitoreo/kpi.csv', index=False)

