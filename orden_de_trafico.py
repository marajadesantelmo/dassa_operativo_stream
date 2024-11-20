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
cursor.execute("""
    SELECT e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing, 
    e.contenedor, e.desc_merc, e.dimension, e.tipo_cnt, e.volumen, e.kilos, env.detalle AS Envase
    FROM [DEPOFIS].[DASSA].[Existente en Stock] e
    JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
existente = pd.DataFrame.from_records(rows, columns=columns)
existente['Envase'] = existente['Envase'].str.title()
#Egresado
cursor.execute(f"""
SELECT  e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing, 
e.contenedor, e.desc_merc,  e.dimension, e.tipo_cnt, e.volumen, e.kilos, env.detalle AS Envase
FROM [DEPOFIS].[DASSA].[Egresadas del stock] e
JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
WHERE e.fecha_egr > '{fecha_ant}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
egresado = pd.DataFrame.from_records(rows, columns=columns)

#Turnos
fecha_inicio = (datetime.now() - timedelta(days=31)).strftime('%Y-%m-%d')
fecha_fin = (datetime.now() + timedelta(days=31)).strftime('%Y-%m-%d')

cursor.execute(f"""
SELECT orden_ing, suborden, renglon, dia, hora, observa, conocim2, destino
FROM DEPOFIS.DASSA.[TURNOSSA]
WHERE dia BETWEEN '{fecha_inicio}' AND '{fecha_fin}'
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
turnos = pd.DataFrame.from_records(rows, columns=columns)
turnos = turnos[turnos['orden_ing'] != 0]
trafico = turnos[turnos['destino'].str.contains('Remision')]

trafico = trafico.copy()
trafico['id'] = trafico[['orden_ing', 'suborden', 'renglon']].astype(str).agg('-'.join, axis=1)

def generate_id_and_cleanup(df):
    df['id'] = df[['orden_ing', 'suborden', 'renglon']].astype(str).agg('-'.join, axis=1)
    df.drop(columns=['orden_ing', 'suborden', 'renglon'], inplace=True)
    return df

existente = generate_id_and_cleanup(existente)
egresado = generate_id_and_cleanup(egresado)

trafico_pendiente = pd.merge(trafico, existente, on='id')
trafico_pendiente['Estado'] = 'Pendiente' 

trafico_realizado = pd.merge(trafico, egresado, on='id')
trafico_realizado['Estado'] = 'Realizado'

trafico = pd.concat([trafico_pendiente, trafico_realizado])


trafico.columns = ['Orden', 'Suborden', 'Renglon',
    'Dia', 'Hora', 'Observacion', 'Conocimiento', 'Tipo Trafico', 'Operacion',
    'Cliente',  'Tipo Operacion', 'Fecha Ingreso', 'Contenedor', 
    'Descripcion Mercaderia', 'Dimension', 'Tipo Contenedor', 
    'Volumen', 'Kilos', 'Envase', 'Estado']

trafico = trafico[['Operacion', 'Dia', 'Hora', 'Observacion', 'Conocimiento', 'Tipo Trafico', 
                    'Cliente', 'Tipo Operacion', 'Fecha Ingreso', 'Contenedor', 
                    'Descripcion Mercaderia', 'Dimension', 'Tipo Contenedor', 
                    'Volumen', 'Kilos', 'Envase', 'Estado']]

trafico.sort_values(by='Dia', inplace=True)

def limpiar_columnas(df):
    columns = ['Observacion', 'Cliente', 'Tipo Operacion', 'Tipo Trafico',
               'Descripcion Mercaderia', 'Envase']
    for column in columns:
        if column in df.columns:
            df[column] = df[column].str.strip()
            df[column] = df[column].str.title()
    return df

trafico = limpiar_columnas(trafico)

trafico['Conocimiento'] = trafico['Conocimiento'].str.strip()

trafico_entrega_vacio = trafico[trafico['Descripcion Mercaderia'].str.contains('Vacio')]

trafico_carga = trafico[(~trafico['Descripcion Mercaderia'].str.contains('Vacio'))]


trafico_entrega_vacio.to_csv(f'{path}data/trafico_entrega_vacio.csv', index=False)
trafico_carga.to_csv(f'{path}data/trafico_carga.csv', index=False)


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