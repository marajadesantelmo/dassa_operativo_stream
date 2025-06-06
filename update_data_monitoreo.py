import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta
from tokens import username, password
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
ultimos_30_dias = datetime.now() - timedelta(days=30)
ultimos_30_dias = ultimos_30_dias.strftime('%Y-%m-%d')

# Querys
cursor.execute("""
SELECT fecha_vto, tp_cpte, aplicacion, adicional, debe, haber
FROM DEPOFIS.DASSA.CtaCcteD
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
saldos_sql= pd.DataFrame.from_records(rows, columns=columns)

cursor.execute(f"""
SELECT Factura, tipo, fecha_emi, fecha_vto, [Neto Gravado], [Neto No Gravado], [Razon Social], vendedor
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
    df['fecha_emi'] = pd.to_datetime(df['fecha_emi'], format='%Y-%m-%d', errors='coerce')
    df['Neto'] = df['Neto Gravado'] + df['Neto No Gravado']
    df.loc[df['tipo'] == 3, 'Factura'] = 'NdC ' + df['Factura'].astype(str)
    df = df.drop(columns=['tipo'])
    df['Razon Social'] = df['Razon Social'].str.strip().str.title()
    df['Razon Social'] = df['Razon Social'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
    df.rename(columns={'fecha_emi': 'Emision', 
                       'vendedor': 'cod_vendedor',
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
    total_saldo = df['Saldo'].sum()
    df.sort_values(by='Saldo', ascending=False, inplace=True)
    df['Saldo'] = df['Saldo'].apply(lambda x: f"${x:,.0f}".replace(",", "."))
    df = df.reset_index(drop=True)
    return df, total_saldo

saldos, total_saldo = transformar_saldos(saldos_sql)

# Fechas para filtros
today = datetime.now()
current_month = datetime.now().replace(day=1)
previous_month = (current_month - timedelta(days=1)).replace(day=1)
same_period_last_month = (current_month - timedelta(days=30)).replace(day=1)
last_12_months = (previous_month- timedelta(days=365)).replace(day=1)

# Ajuste por inflacion
ipc = pd.read_excel('ipc_mensual.xlsx')
facturacion['Mes'] = facturacion['Emision'].dt.strftime('%m-%Y')
facturacion = pd.merge(facturacion, ipc, left_on='Mes', right_on='periodo', how='left')
facturacion['Importe Total'] = facturacion['Importe Total'].astype(int)
facturacion['Ajustado'] = facturacion['Importe Total'] * (100 / facturacion['ipc'])
facturacion['Ajustado'] = facturacion['Ajustado'].round(0).astype(int)

#Ventas totales por mes
ventas_totales_por_mes = facturacion.groupby('Mes').agg({'Importe Total': 'sum', 'Ajustado': 'sum'}).reset_index()
ventas_totales_por_mes['Mes'] = pd.to_datetime(ventas_totales_por_mes['Mes'], format='%m-%Y').dt.strftime('%Y-%m')

ventas_totales_por_mes_tabla = ventas_totales_por_mes.copy()
ventas_totales_por_mes_tabla['Importe Total'] = ventas_totales_por_mes_tabla['Importe Total'].apply(lambda x: f"${x:,.0f}")
ventas_totales_por_mes_tabla['Ajustado'] = ventas_totales_por_mes_tabla['Ajustado'].apply(lambda x: f"${x:,.0f}")
ventas_totales_por_mes_tabla = ventas_totales_por_mes_tabla.sort_values(by='Mes', ascending=False)
ventas_totales_por_mes_tabla.rename(columns={'Mes': 'Mes', 'Importe Total': 'Ventas Total', 'Ajustado': 'Ajustado'}, inplace=True)

ventas_totales_por_mes_grafico = ventas_totales_por_mes[['Mes', 'Ajustado']]

# Filter data for KPIs
current_month_sales = facturacion[(facturacion['Emision'] >= current_month.strftime('%Y-%m-%d'))]

current_month_sales[current_month_sales['Importe Total'] != current_month_sales['Ajustado']]

previous_month_sales = facturacion[(facturacion['Emision'] >= previous_month.strftime('%Y-%m-%d')) & (facturacion['Emision'] < current_month.strftime('%Y-%m-%d'))]
same_period_last_month_sales = facturacion[(facturacion['Emision'] >= same_period_last_month.strftime('%Y-%m-%d')) & (facturacion['Emision'] < (same_period_last_month + timedelta(days=today.day)).strftime('%Y-%m-%d'))]
last_12_months_sales = facturacion[(facturacion['Emision'] >= last_12_months.strftime('%Y-%m-%d')) & (facturacion['Emision'] < current_month.strftime('%Y-%m-%d'))]
last_30_days = facturacion[(facturacion['Emision'] >= ultimos_30_dias)]

# Calculate totals
current_month_total = round(current_month_sales['Importe Total'].sum(), 0)
previous_month_total = round(previous_month_sales['Importe Total'].sum(), 0)
same_period_last_month_total = round(same_period_last_month_sales['Importe Total'].sum(), 0)
monthly_average_last_12_months = round(last_12_months_sales['Ajustado'].sum() / 12, 0)



# Ventas por cliente

ventas_por_cliente_total = facturacion.groupby('Razon Social').agg({'Importe Total': 'sum'}).reset_index()
ventas_por_cliente_total = ventas_por_cliente_total.sort_values(by='Importe Total', ascending=False)
ventas_por_cliente_total['Importe Total'] = ventas_por_cliente_total['Importe Total'].round(0)


ventas_por_cliente_mes_actual = current_month_sales.groupby('Razon Social').agg({'Importe Total': 'sum'}).reset_index()
ventas_por_cliente_mes_anterior = previous_month_sales.groupby('Razon Social').agg({'Importe Total': 'sum'}).reset_index()
ventas_por_cliente = ventas_por_cliente_mes_actual.merge(ventas_por_cliente_mes_anterior, on='Razon Social', how='outer', suffixes=('_actual', '_anterior'))
ventas_por_cliente = ventas_por_cliente.fillna(0)
ventas_por_cliente['%'] = (ventas_por_cliente['Importe Total_actual'] / ventas_por_cliente['Importe Total_actual'].sum() * 100).fillna(0)
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
ventas_por_vendedor = ventas_por_vendedor_mes_anterior.merge(ventas_por_vendedor_mes_actual, on='nombre_vendedor', how='outer', suffixes=('_anterior', '_actual'))
ventas_por_vendedor = ventas_por_vendedor.fillna(0)
ventas_por_vendedor['%'] = (ventas_por_vendedor['Importe Total_actual'] / ventas_por_vendedor['Importe Total_actual'].sum() * 100).fillna(0)
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

cursor.execute("""
    SELECT volumen
    FROM DEPOFIS.DASSA.[Existente en Stock]
    WHERE suborden !=0
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
existente = pd.DataFrame.from_records(rows, columns=columns)
vol_existente = existente['volumen'].sum()
ocupacion = vol_existente / 13460
ocupacion = f"{ocupacion:.1%}".replace(".", ",")

existente = pd.DataFrame({
    'Metricas': ['Volumen Existente', 'Ocupación'],
    'Valores': [vol_existente, ocupacion]
})

#%% Operativo - CNTs Expo
print('Metricas mensuales de operativo')
#Egresado
cursor.execute("""
SELECT  e.fecha_egr, e.orden_ing, e.suborden, e.renglon, e.tipo_oper, e.contenedor
FROM [DEPOFIS].[DASSA].[Egresadas del stock] e
JOIN [DEPOFIS].[DASSA].[Tip_env] env ON e.tipo_env = env.codigo
WHERE e.fecha_egr > '2021-01-01'
AND e.tipo_oper = 'EXPORTACION'
AND e.suborden = 0
AND env.detalle = 'CONTENEDOR'
""") 

rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
egresado = pd.DataFrame.from_records(rows, columns=columns)
egresado['contenedor'] = egresado['contenedor'].str.strip()
egresado = egresado[egresado['contenedor'].notna() & (egresado['contenedor'] != '') & (egresado['contenedor'] != '-      -')]
egresado = egresado.drop_duplicates(subset=['contenedor'], keep='first')
egresado['fecha_egr'] = pd.to_datetime(egresado['fecha_egr'], errors='coerce')
egresado = egresado.dropna(subset=['fecha_egr'])
egresado['Mes'] = egresado['fecha_egr'].dt.to_period('M')

cnts_expo_egr_mensual = egresado.groupby('Mes')['contenedor'].count().reset_index()
cnts_expo_egr_mensual.columns = ['Mes', 'CNTs Expo']

cnts_expo_egr_mes_actual = egresado[(egresado['fecha_egr'] >= current_month) & (egresado['fecha_egr'] <= today)]
cnts_expo_egr_mes_actual = cnts_expo_egr_mes_actual['contenedor'].count()

cnts_expo_egr_mes_anterior = egresado[(egresado['fecha_egr'] >= first_day_prev_month) & (egresado['fecha_egr'] <= last_day_prev_month)]
cnts_expo_egr_mes_anterior  = cnts_expo_egr_mes_anterior ['contenedor'].count()

cnts_expo_egr_promedio_mensual = cnts_expo_egr_mensual['CNTs Expo'].mean().round(0).astype(int)

days_passed_current_month = (today - current_month).days + 1
prom_dia_expo = cnts_expo_egr_mes_actual / days_passed_current_month
ctn_expo_proyectado = prom_dia_expo * 31
ctn_expo_proyectado = ctn_expo_proyectado.round(0).astype(int)



#%% Operativo CNTs IMPO

#Ingresado
cursor.execute("""
SELECT  i.fecha_ing, i.orden_ing, i.suborden, i.renglon, i.tipo_oper, i.contenedor, i.fecha_desc
FROM DEPOFIS.DASSA.[Ingresadas En Stock] i
JOIN DEPOFIS.DASSA.[Tip_env] env ON i.tipo_env = env.codigo
WHERE fecha_ing > '2021-01-01'
AND tipo_oper = 'IMPORTACION'
AND suborden = 0
AND env.detalle = 'CONTENEDOR'
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ingresado = pd.DataFrame.from_records(rows, columns=columns)
ingresado['contenedor'] = ingresado['contenedor'].str.strip()
ingresado = ingresado[ingresado['contenedor'].notna() & (ingresado['contenedor'] != '') & (ingresado['contenedor'] != '-      -')]
ingresado = ingresado.drop_duplicates(subset=['contenedor'], keep='first')
ingresado['fecha_ing'] = pd.to_datetime(ingresado['fecha_ing'], errors='coerce')
ingresado = ingresado.dropna(subset=['fecha_ing'])
ingresado['Mes'] = ingresado['fecha_ing'].dt.to_period('M')
ingresado['Desconsolida'] = ingresado['fecha_desc'].apply(lambda x: "T" if x == '1899-12-30' else "TD")
cnts_impo_ing_mensual = ingresado.groupby('Mes')['contenedor'].count().reset_index()
cnts_impo_ing_mensual.columns = ['Mes', 'CNTs Impo']
cnts_impo_ing_mes_actual = ingresado[(ingresado['fecha_ing'] >= current_month) & (ingresado['fecha_ing'] <= today)]['contenedor'].count()
cnts_impo_ing_mes_anterior = ingresado[(ingresado['fecha_ing'] >= first_day_prev_month) & (ingresado['fecha_ing'] <= last_day_prev_month)]
cnts_impo_ing_mes_anterior  = cnts_impo_ing_mes_anterior ['contenedor'].count()
cnts_impo_ing_promedio_mensual = cnts_impo_ing_mensual['CNTs Impo'].mean().round(0).astype(int)
prom_dia_impo = cnts_impo_ing_mes_actual / days_passed_current_month
ctn_impo_proyectado = prom_dia_impo * 31
ctn_impo_proyectado = ctn_impo_proyectado.round(0).astype(int)
resumen_mensual_ctns = pd.merge(cnts_expo_egr_mensual, cnts_impo_ing_mensual, on='Mes')
resumen_mensual_ctns = resumen_mensual_ctns[resumen_mensual_ctns['Mes'] != current_month.strftime('%Y-%m')]

cnts_mes_actual= ingresado[(ingresado['fecha_ing'] >= current_month) & (ingresado['fecha_ing'] <= today)]
desconsolida_percentage = (cnts_mes_actual['Desconsolida'] == 'TD').mean() * 100
desconsolida_percentage = f"{desconsolida_percentage:.1f} %".replace(".", ",")
desconsolida_mes_actual = (cnts_mes_actual['Desconsolida'] == 'TD').sum()

# Monthly data on containers inbound disaggregated by Desconsolida
cnts_impo_ing_mensual_desconsolida = ingresado.groupby(['Mes', 'Desconsolida']).agg({'contenedor': 'count'}).reset_index()
cnts_impo_ing_mensual_desconsolida = cnts_impo_ing_mensual_desconsolida.pivot(index='Mes', columns='Desconsolida', values='contenedor').fillna(0)
cnts_impo_ing_mensual_desconsolida['Total'] = cnts_impo_ing_mensual_desconsolida.sum(axis=1)
cnts_impo_ing_mensual_desconsolida['% TD'] = (cnts_impo_ing_mensual_desconsolida['TD'] / cnts_impo_ing_mensual_desconsolida['Total'] * 100).round(1).astype(str) + '%'
cnts_impo_ing_mensual_desconsolida['% T'] = (cnts_impo_ing_mensual_desconsolida['T'] / cnts_impo_ing_mensual_desconsolida['Total'] * 100).round(1).astype(str) + '%'
cnts_impo_ing_mensual_desconsolida.drop(columns = ['Total'], inplace=True)
cnts_impo_ing_mensual_desconsolida.reset_index(inplace=True)


# Comparativa mensual
# Compare same month by month for this year and last year
resumen_mensual_ctns['Year'] = resumen_mensual_ctns['Mes'].dt.year
resumen_mensual_ctns['Month'] = resumen_mensual_ctns['Mes'].dt.month
this_year = today.year
last_year = today.year - 1
resumen_mensual_ctns = resumen_mensual_ctns[(resumen_mensual_ctns['Year'] == this_year) | (resumen_mensual_ctns['Year'] == last_year)]
resumen_mensual_ctns_expo = resumen_mensual_ctns[['CNTs Expo', 'Year', 'Month']]
resumen_mensual_ctns_impo = resumen_mensual_ctns[['CNTs Impo', 'Year', 'Month']]
resumen_mensual_ctns = resumen_mensual_ctns[['Mes', 'CNTs Expo', 'CNTs Impo']]
resumen_mensual_ctns_impo = resumen_mensual_ctns_impo.pivot(index='Month', columns='Year', values=['CNTs Impo'])
resumen_mensual_ctns_impo.columns = [f"{col[0]} {col[1]}" for col in resumen_mensual_ctns_impo.columns]
resumen_mensual_ctns_impo.reset_index(inplace=True)
resumen_mensual_ctns_impo['Dif'] = resumen_mensual_ctns_impo['CNTs Impo ' + str(this_year)] - resumen_mensual_ctns_impo['CNTs Impo ' + str(last_year)]
resumen_mensual_ctns_impo['CNTs Impo ' + str(this_year)] = resumen_mensual_ctns_impo['CNTs Impo ' + str(this_year)].fillna(0).astype(int).astype(str)
resumen_mensual_ctns_impo['Dif'] = resumen_mensual_ctns_impo['Dif'].fillna(0)
resumen_mensual_ctns_impo.rename(columns={'Month': 'Mes'}, inplace=True)
resumen_mensual_ctns_expo = resumen_mensual_ctns_expo.pivot(index='Month', columns='Year', values=['CNTs Expo'])
resumen_mensual_ctns_expo.columns = [f"{col[0]} {col[1]}" for col in resumen_mensual_ctns_expo.columns]
resumen_mensual_ctns_expo.reset_index(inplace=True)
resumen_mensual_ctns_expo['Dif'] = resumen_mensual_ctns_expo['CNTs Expo ' + str(this_year)] - resumen_mensual_ctns_expo['CNTs Expo ' + str(last_year)]
resumen_mensual_ctns_expo['CNTs Expo ' + str(this_year)] = resumen_mensual_ctns_expo['CNTs Expo ' + str(this_year)].fillna(0).astype(int).astype(str)
resumen_mensual_ctns_expo['Dif'] = resumen_mensual_ctns_expo['Dif'].fillna(0)
resumen_mensual_ctns_expo.rename(columns={'Month': 'Mes'}, inplace=True)

#%% Clientes nuevos
print('Clientes nuevos')
cursor.execute(f"""
SELECT  apellido, fecha_alta, vendedor, clie_nro, consolida, nombre
FROM DEPOFIS.DASSA.[Clientes]
WHERE fecha_alta >= '{ultimos_30_dias}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
clientes_nuevos= pd.DataFrame.from_records(rows, columns=columns)

clientes_nuevos['apellido'] = clientes_nuevos['apellido'].str.strip().str.title()
clientes_nuevos['apellido'] = clientes_nuevos['apellido'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
cliente_nuevos = clientes_nuevos[['apellido', 'fecha_alta', 'vendedor']]
ventas_clientes_nuevos = pd.merge(clientes_nuevos, ventas_por_cliente_total, left_on='apellido', right_on='Razon Social', how='inner')

total_ventas_clientes_nuevos = ventas_clientes_nuevos['Importe Total'].sum()
total_ventas_clientes_nuevos = round(total_ventas_clientes_nuevos, 0)


ventas_clientes_nuevos['Importe Total'] = ventas_clientes_nuevos['Importe Total'].apply(lambda x: f"${x:,.0f}")
ventas_clientes_nuevos = ventas_clientes_nuevos.rename(columns={'Razon Social': 'Cliente', 'Importe Total': 'Venta Total'})
ventas_clientes_nuevos.reset_index(drop=True, inplace=True)
ventas_clientes_nuevos = pd.merge(ventas_clientes_nuevos, diccionario_vendedores, left_on='vendedor', right_on='cod_vendedor', how='left')
ventas_clientes_nuevos.rename(columns={'fecha_alta': 'Fecha Alta'}, inplace=True)
ventas_clientes_nuevos = ventas_clientes_nuevos[['Cliente', 'Fecha Alta', 'Vendedor', 'Venta Total']]
ventas_clientes_nuevos = ventas_clientes_nuevos.sort_values(by='Fecha Alta', ascending=False)


# Volumen ingresado
cursor.execute("""
SELECT  fecha_ing, orden_ing, suborden, renglon, volumen, tipo_oper
FROM DEPOFIS.DASSA.[Ingresadas En Stock]
WHERE fecha_ing > '2024-01-01'
AND suborden != 0
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ingresado = pd.DataFrame.from_records(rows, columns=columns)
ingresado['fecha_ing'] = pd.to_datetime(ingresado['fecha_ing'], errors='coerce')
ingresado = ingresado.dropna(subset=['fecha_ing'])
ingresado['Mes'] = ingresado['fecha_ing'].dt.to_period('M')
volumen_ingresado_mensual = ingresado.groupby(['Mes', 'tipo_oper'])['volumen'].sum().reset_index()
volumen_ingresado_mensual.columns = ['Mes', 'Tipo Operación', 'Volumen']
volumen_ingresado_mensual['Tipo Operación'] = volumen_ingresado_mensual['Tipo Operación'].str.strip().str.title()
volumen_impo_ingresado_mes_actual = volumen_ingresado_mensual[(volumen_ingresado_mensual['Mes'] == current_month.strftime('%Y-%m')) & (volumen_ingresado_mensual['Tipo Operación'] == 'Importacion')]['Volumen'].sum()
volumen_expo_ingresado_mes_actual = volumen_ingresado_mensual[(volumen_ingresado_mensual['Mes'] == current_month.strftime('%Y-%m')) & (volumen_ingresado_mensual['Tipo Operación'] == 'Exportacion')]['Volumen'].sum()

# Volumen egresado
cursor.execute("""
SELECT  fecha_egr, orden_ing, suborden, renglon, tipo_oper, volumen
FROM [DEPOFIS].[DASSA].[Egresadas del stock]
WHERE fecha_egr > '2024-01-01'
AND suborden != 0
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
egresado = pd.DataFrame.from_records(rows, columns=columns)
egresado['fecha_egr'] = pd.to_datetime(egresado['fecha_egr'], errors='coerce')
egresado = egresado.dropna(subset=['fecha_egr'])
egresado['Mes'] = egresado['fecha_egr'].dt.to_period('M')
volumen_egresado_mensual = egresado.groupby(['Mes', 'tipo_oper'])['volumen'].sum().reset_index()
volumen_egresado_mensual.columns = ['Mes', 'Tipo Operación', 'Volumen']
volumen_egresado_mensual['Tipo Operación'] = volumen_egresado_mensual['Tipo Operación'].str.strip().str.title()
volumen_impo_egresado_mes_actual = volumen_egresado_mensual[(volumen_egresado_mensual['Mes'] == current_month.strftime('%Y-%m')) & (volumen_egresado_mensual['Tipo Operación'] == 'Importacion')]['Volumen'].sum()
volumen_expo_egresado_mes_actual = volumen_egresado_mensual[(volumen_egresado_mensual['Mes'] == current_month.strftime('%Y-%m')) & (volumen_egresado_mensual['Tipo Operación'] == 'Exportacion')]['Volumen'].sum()


#Dataframes con kpis de importacion y exportacion
kpi_data_impo = [
    ['Mes actual', 'Mes anterior', 'Promedio mensual', 'Proyeccion mes actual', 'Vol. Ingresado', 'Vol. Egresado', 'Desco. mes actual', 'Desco. %'],
    [cnts_impo_ing_mes_actual , cnts_impo_ing_mes_anterior, cnts_impo_ing_promedio_mensual, 
     ctn_impo_proyectado, volumen_impo_ingresado_mes_actual, -volumen_impo_egresado_mes_actual, 
     desconsolida_mes_actual, desconsolida_percentage]
]
kpi_impo_df = pd.DataFrame(kpi_data_impo[1:], columns=kpi_data_impo[0])


kpi_data_expo = [
    ['Mes actual', 'Mes anterior', 'Promedio mensual', 'Proyeccion mes actual', 'Vol. Ingresado', 'Vol. Egresado'],
    [cnts_expo_egr_mes_actual , cnts_expo_egr_mes_anterior, cnts_expo_egr_promedio_mensual, 
    ctn_expo_proyectado, volumen_expo_ingresado_mes_actual, -volumen_expo_egresado_mes_actual]
]

kpi_expo_df = pd.DataFrame(kpi_data_expo[1:], columns=kpi_data_expo[0])


# KPIs ventas y saldos
kpis = pd.DataFrame({
    'Metric': ['Mes actual', 'Mes anterior', 'Mismo periodo mes anterior', 'Prom. mensual ajustado', 'Venta total clientes nuevos', 'Saldo total'],
    'Value': [current_month_total, previous_month_total, same_period_last_month_total, monthly_average_last_12_months, total_ventas_clientes_nuevos, total_saldo]
})

kpis['Value'] = kpis['Value'].apply(lambda x: f"${x:,.0f}".replace(",", "."))

print(kpis)


#### GUARDO DATOS

kpis.to_csv('data/monitoreo/kpi.csv', index=False)
ventas_por_vendedor.to_csv('data/monitoreo/ventas_por_vendedor.csv', index=False)
ventas_por_cliente.to_csv('data/monitoreo/ventas_por_cliente.csv', index=False)
saldos.to_csv('data/monitoreo/saldos.csv', index=False)
existente.to_csv('data/monitoreo/existente.csv', index=False)
resumen_mensual_ctns.to_csv('data/monitoreo/resumen_mensual_ctns.csv', index=False)
kpi_impo_df.to_csv('data/monitoreo/kpi_data_impo.csv', index=False)
kpi_expo_df.to_csv('data/monitoreo/kpi_data_expo.csv', index=False)
ventas_clientes_nuevos.to_csv('data/monitoreo/ventas_clientes_nuevos.csv', index=False)
resumen_mensual_ctns_expo.to_csv('data/monitoreo/resumen_mensual_ctns_expo.csv', index=False)
resumen_mensual_ctns_impo.to_csv('data/monitoreo/resumen_mensual_ctns_impo.csv', index=False)
volumen_ingresado_mensual.to_csv('data/monitoreo/volumen_ingresado_mensual.csv', index=False)  
volumen_egresado_mensual.to_csv('data/monitoreo/volumen_egresado_mensual.csv', index=False)
ventas_totales_por_mes_tabla.to_csv('data/monitoreo/ventas_totales_por_mes_tabla.csv', index=False)
ventas_totales_por_mes_grafico.to_csv('data/monitoreo/ventas_totales_por_mes_grafico.csv', index=False)
cnts_impo_ing_mensual_desconsolida.to_csv('data/monitoreo/cnts_impo_ing_mensual_desconsolida.csv', index=False)


conn.close()
gc = gspread.service_account(filename='//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/credenciales_gsheets.json')
sheet_logs =  gc.open_by_url('https://docs.google.com/spreadsheets/d/1aPUkhige3tq7_HuJezTYA1Ko7BWZ4D4W0sZJtsTyq3A')                                           
worksheet_logs = sheet_logs.worksheet('Logeos')
df_logs = worksheet_logs.get_all_values()
df_logs = pd.DataFrame(df_logs[1:], columns=df_logs[0])
now = datetime.now().strftime('%Y-%m-%d %H:%M')
new_log_entry = pd.DataFrame([{'Rutina': 'Streamlit - Update Data Monitoreo', 'Fecha y Hora': now}])
df_logs = pd.concat([df_logs, new_log_entry], ignore_index=True)
worksheet_logs.clear()
set_with_dataframe(worksheet_logs, df_logs)
print("Se registró el logeo")