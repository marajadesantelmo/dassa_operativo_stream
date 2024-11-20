import pyodbc
import pandas as pd
from datetime import datetime, timedelta
import gspread
from gspread_dataframe import set_with_dataframe
import time
from tokens import username, password

path = '//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/'

print('Descargando datos de SQL')
server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

fecha = datetime.now().strftime('%Y-%m-%d')
fecha_ant = datetime.now() - timedelta(days=120)
fecha_ant = fecha_ant.strftime('%Y-%m-%d')
print('Bajando datos de SQL Server...')
#Existente

'''
Script que actualiza los csv
'''
import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta
from tokens import username, password
from utils import rellenar_df_vacio
import gspread
from gspread_dataframe import set_with_dataframe
from datetime import datetime

if os.path.exists('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream'):
    os.chdir('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream')
elif os.path.exists('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream'):
    os.chdir('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream')
else:
    print("Se usa working directory por defecto")

path = '//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/'

### ARRIBOS ####

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

#%% Arribos

#Descargo EXPO a arribar
cursor.execute(f"""
SELECT c.orden, c.fecha, c.contenedor, c.terminal, c.turno, c.dimension, c.tipo_cnt, c.operacion, 
               c.cliente, c.precinto, c.bookings, c.peso, c.observacio, c.arribado, c.camion, c.empresa, c.chofer, c.doc_tipo, c.doc_num, c.chapa_trac, 
               c.chapa_semi, c.hora_ing, c.hora, c.despachant, c.consignat, c.tipo_oper, c.vto_vacio, c.zona, c.desc_merc, c.permemb,
       cl.apellido AS cliente, c.desc_merc, c.precinto, c.dimension, c.hora_ing
FROM [DEPOFIS].[DASSA].[CORDICAR] c
JOIN DEPOFIS.DASSA.[Clientes] cl ON c.cliente = cl.clie_nro
WHERE c.tipo_oper = 'VACIO' 
AND c.fecha >= '{fecha}'
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
arribos_vacios = pd.DataFrame.from_records(rows, columns=columns)

arribos_vacios['terminal'] = arribos_vacios['terminal'].astype(str)
terminal_mapping = {
    '10057': 'TRP',
    '10073': 'Exolgan',
    '10068': 'Terminal 4'}
arribos_vacios['terminal'] = arribos_vacios['terminal'].replace(terminal_mapping)
arribos_vacios['contenedor'] = arribos_vacios['contenedor'].str.strip()
arribos_vacios['bookings'] = arribos_vacios['bookings'].str.strip()
arribos_vacios['operacion'] = arribos_vacios['operacion'].str.strip()
arribos_vacios['tipo_oper'] = arribos_vacios['tipo_oper'].str.strip()
arribos_vacios['desc_merc'] = arribos_vacios['desc_merc'].str.strip()
arribos_vacios['Contenedor2'] = arribos_vacios['contenedor'].str.strip()    # Ver para que contenedor2
arribos_vacios['cliente'] = arribos_vacios['cliente'].str.strip()
arribos_vacios['cliente'] =  arribos_vacios['cliente'].str.title()
arribos_vacios['Estado'] = arribos_vacios['arribado'].replace({0: 'Pendiente', 1: 'Arribado'})
arribos_vacios.loc[arribos_vacios['Estado'] == 'Arribado', 'Estado'] = arribos_vacios['hora_ing'].astype(str) + ' Arribado'
arribos_vacios['fecha'] = pd.to_datetime(arribos_vacios['fecha']).dt.strftime('%d/%m')
arribos_vacios = arribos_vacios.sort_values(by='fecha')
arribos_vacios['contenedor'] = arribos_vacios['contenedor'].apply(lambda x: '-' if x.strip() == '' else x.strip())
arribos_vacios['contenedor'] = arribos_vacios['contenedor'].str.strip()
arribos_vacios['contenedor'] = arribos_vacios['contenedor'].fillna('-')
arribos_vacios['cliente'] = arribos_vacios['cliente'].fillna('').apply(lambda x: x[:30] + "..." if len(x) > 30 else x)
arribos_vacios['desc_merc'] = arribos_vacios['desc_merc'].str.strip()
arribos_vacios['desc_merc'] = arribos_vacios['desc_merc'].fillna('').apply(lambda x: x[:30] + "..." if len(x) > 30 else x)

arribos_vacios.to_csv(f'{path}data/trafico_arribos_vacios.csv', index=False)

gc = gspread.service_account(filename='//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/credenciales_gsheets.json')
sheet_logs =  gc.open_by_url('https://docs.google.com/spreadsheets/d/1aPUkhige3tq7_HuJezTYA1Ko7BWZ4D4W0sZJtsTyq3A')                                           
worksheet_logs = sheet_logs.worksheet('Logeos')
df_logs = worksheet_logs.get_all_values()
df_logs = pd.DataFrame(df_logs[1:], columns=df_logs[0])
now = datetime.now().strftime('%Y-%m-%d %H:%M')
new_log_entry = pd.DataFrame([{'Rutina': 'Streamlit - Orden de trafico', 'Fecha y Hora': now}])
df_logs = pd.concat([df_logs, new_log_entry], ignore_index=True)
worksheet_logs.clear()
set_with_dataframe(worksheet_logs, df_logs)
print("Se registró el logeo")