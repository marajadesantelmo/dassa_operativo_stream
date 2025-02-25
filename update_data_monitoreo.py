import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta
from tokens import username, password

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
AND concepto < 60026
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
facturacion_sql = pd.DataFrame.from_records(rows, columns=columns)

# Procesamientos dataframes
print('Procesando datos')

def transformar_facturacion(df): 
    df['fecha_emi'] = pd.to_datetime(df['fecha_emi'])
    df = df[df['fecha_emi'] > pd.to_datetime(fecha_ant)].copy()
    df['Neto'] = df['Neto Gravado'] + df['Neto No Gravado']
    df.loc[df['tipo'] == 3, 'Factura'] = 'NdC ' + df['Factura'].astype(str)
    df = df.drop(columns=['tipo'])
    df = df.groupby(
        ['Razon Social']).agg({
        'Neto': 'sum',
        'vendedor': 'first'}).reset_index()
    df['Razon Social'] = df['Razon Social'].str.strip().str.title()
    df['Razon Social'] = df['Razon Social'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
    df.rename(columns={'vendedor': 'cod_vendedor', 
                       'Neto': 'Importe Total'}, inplace=True)
    return df

facturacion = transformar_facturacion(facturacion_sql)
diccionario_vendedores = pd.read_excel(path + 'diccionario_vendedores_puros_dassa.xlsx')
facturacion = facturacion.merge(diccionario_vendedores, on='cod_vendedor', how='left')

def transformar_saldos(df): 
    df['saldo'] = df['debe'] - df['haber']
    df = df.groupby(['aplicacion']).agg({'tp_cpte': 'first', 
                                         'adicional': 'first', 
                                         'fecha_vto': 'first', 
                                         'saldo': 'sum'}).reset_index()
    df = df[df['saldo'] > 1]
    df['adicional'] = df['adicional'].str.strip().str.title()
    df.rename(columns={'tp_cpte': 'Tipo cpte', 
                       'adicional': 'Cliente', 
                       'fecha_vto': 'Vencimiento', 
                       'saldo': 'Saldo', 
                       'aplicacion': 'Comprobante'}, 
                       inplace=True)
    df = df.groupby(['Cliente']).agg({'Saldo': 'sum'}).reset_index()
    df['Saldo'] = df['Saldo'].round(0)
    df.sort_values(by='Saldo', ascending=False, inplace=True)
    df['Saldo'] = df['Saldo'].apply(lambda x: f"${x:,.0f}".replace(",", "."))
    df = df.reset_index(drop=True)
    return df

saldos = transformar_saldos(saldos_sql)

# Calculate sales KPIs
today = datetime.now()
current_month = datetime.now().replace(day=1)
previous_month = (current_month - timedelta(days=1)).replace(day=1)
same_period_last_month = (current_month - timedelta(days=30)).replace(day=1)
last_12_months = (current_month - timedelta(days=365)).replace(day=1)

# Filter data for KPIs
current_month_sales = facturacion[(facturacion['Emision'] >= current_month.strftime('%Y-%m-%d'))]
previous_month_sales = facturacion[(facturacion['Emision'] >= previous_month.strftime('%Y-%m-%d')) & (facturacion['Emision'] < current_month.strftime('%Y-%m-%d'))]
same_period_last_month_sales = facturacion[(facturacion['Emision'] >= same_period_last_month.strftime('%Y-%m-%d')) & (facturacion['Emision'] < (same_period_last_month + timedelta(days=today.day)).strftime('%Y-%m-%d'))]
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
ventas_por_cliente['%'] = (ventas_por_cliente['Importe Total_actual'] / ventas_por_cliente['Importe Total_actual'].sum() * 100)
ventas_por_cliente['%'] = ventas_por_cliente['%'].apply(lambda x: f"{x:,.1f}".replace(".", ","))
ventas_por_cliente['Importe Total_actual'] = ventas_por_cliente['Importe Total_actual'].round(0)
ventas_por_cliente['Importe Total_anterior'] = ventas_por_cliente['Importe Total_anterior'].round(0)
ventas_por_cliente.rename(columns={'Razon Social': 'Cliente', 
                       'Importe Total_actual': 'Mes actual', 
                       'Importe Total_anterior': 'Mes anterior'}, inplace=True)
ventas_por_cliente = ventas_por_cliente.sort_values(by='Mes actual', ascending=False)
ventas_por_cliente['Mes actual'] = ventas_por_cliente['Mes actual'].apply(lambda x: f"${x:,.0f}")
ventas_por_cliente['Mes anterior'] = ventas_por_cliente['Mes anterior'].apply(lambda x: f"${x:,.0f}")
ventas_por_cliente = ventas_por_cliente[['Cliente', 'Mes anterior', 'Mes actual', '%']]
ventas_por_cliente.reset_index(drop=True, inplace=True)
print(ventas_por_cliente)

# Ventas por vendedor
ventas_por_vendedor_mes_actual = current_month_sales.groupby('nombre_vendedor').agg({'Importe Total': 'sum'}).reset_index()
ventas_por_vendedor_mes_anterior = previous_month_sales.groupby('nombre_vendedor').agg({'Importe Total': 'sum'}).reset_index()
ventas_por_vendedor = ventas_por_vendedor_mes_anterior.merge(ventas_por_vendedor_mes_actual, on='nombre_vendedor', how='outer', suffixes=('_actual', '_anterior'))
ventas_por_vendedor = ventas_por_vendedor.fillna(0)
ventas_por_vendedor['%'] = (ventas_por_vendedor['Importe Total_actual'] / ventas_por_vendedor['Importe Total_actual'].sum() * 100)
ventas_por_vendedor['%'] = ventas_por_vendedor['%'].apply(lambda x: f"{x:,.1f}".replace(".", ","))
ventas_por_vendedor['Importe Total_actual'] = ventas_por_vendedor['Importe Total_actual'].round(0)
ventas_por_vendedor['Importe Total_anterior'] = ventas_por_vendedor['Importe Total_anterior'].round(0)
ventas_por_vendedor.rename(columns={'nombre_vendedor': 'Vendedor', 
                       'Importe Total_anterior': 'Mes anterior',
                       'Importe Total_actual': 'Mes actual' }, inplace=True)
ventas_por_vendedor = ventas_por_vendedor.sort_values(by='Mes actual', ascending=False)
ventas_por_vendedor['Mes actual'] = ventas_por_vendedor['Mes actual'].apply(lambda x: f"${x:,.0f}").replace(",", ".")
ventas_por_vendedor['Mes anterior'] = ventas_por_vendedor['Mes anterior'].apply(lambda x: f"${x:,.0f}").replace(",", ".")
ventas_por_vendedor = ventas_por_vendedor[['Vendedor', 'Mes anterior', 'Mes actual', '%']]
ventas_por_vendedor.reset_index(drop=True, inplace=True)
print(ventas_por_vendedor)

kpis.to_csv('data/monitoreo/kpi.csv', index=False)
ventas_por_vendedor.to_csv('data/monitoreo/ventas_por_vendedor.csv', index=False)
ventas_por_cliente.to_csv('data/monitoreo/ventas_por_cliente.csv', index=False)
saldos.to_csv('data/monitoreo/saldos.csv', index=False)

