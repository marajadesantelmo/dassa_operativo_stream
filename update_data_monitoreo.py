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

cursor.execute(f"""
SELECT Factura, tipo, fecha_emi, fecha_vto, [Neto Gravado], [Neto No Gravado], [Importe Total], [Razon Social]
FROM DEPOFIS.DASSA.Facturacion
WHERE fecha_emi > '2024-01-01'
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
facturacion = pd.DataFrame.from_records(rows, columns=columns)

# Calculate sales KPIs
current_month = datetime.now().replace(day=1)
previous_month = (current_month - timedelta(days=1)).replace(day=1)
same_period_last_month = (current_month - timedelta(days=30)).replace(day=1)
last_12_months = (current_month - timedelta(days=365)).replace(day=1)

# Filter data for KPIs
current_month_sales = facturacion[(facturacion['fecha_emi'] >= current_month.strftime('%Y-%m-%d'))]
previous_month_sales = facturacion[(facturacion['fecha_emi'] >= previous_month.strftime('%Y-%m-%d')) & (facturacion['fecha_emi'] < current_month.strftime('%Y-%m-%d'))]
same_period_last_month_sales = facturacion[(facturacion['fecha_emi'] >= same_period_last_month.strftime('%Y-%m-%d')) & (facturacion['fecha_emi'] < (same_period_last_month + timedelta(days=30)).strftime('%Y-%m-%d'))]
last_12_months_sales = facturacion[(facturacion['fecha_emi'] >= last_12_months.strftime('%Y-%m-%d'))]

# Calculate totals
current_month_total = current_month_sales['Importe Total'].sum()
previous_month_total = previous_month_sales['Importe Total'].sum()
same_period_last_month_total = same_period_last_month_sales['Importe Total'].sum()
monthly_average_last_12_months = last_12_months_sales['Importe Total'].sum() / 12

# Create KPIs dataframe
kpis = pd.DataFrame({
    'Metric': ['Mes actual', 'Mes anterior', 'Mismo periodo mes anterior', 'Promedio mensual ultimos 12 meses'],
    'Value': [current_month_total, previous_month_total, same_period_last_month_total, monthly_average_last_12_months]
})

print(kpis)

kpis.to_csv('data/monitoreo/kpi.csv', index=False)

