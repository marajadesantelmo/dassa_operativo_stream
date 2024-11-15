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
fecha_ant1 = datetime.now() - timedelta(days=120)
fecha_ant1 = fecha_ant1.strftime('%Y-%m-%d')
fecha_ant = datetime.now() - timedelta(days=120)
fecha_ant = fecha_ant.strftime('%Y-%m-%d')
fecha_ant_ult3dias = datetime.now() - timedelta(days=3)
fecha_ant_ult3dias = fecha_ant_ult3dias.strftime('%Y-%m-%d')

#%% Arribos
#Descargo contenedores IMPO a arribar
cursor.execute(f"""
    SELECT c.contenedor, c.buque, c.terminal, c.fecha, c.turno,  c.peso,  c.operacion, 
           c.arribado, c.dimension, c.tipo_cnt, c.despachant, c.precinto, c.bookings,  cl.apellido AS cliente
    FROM [DEPOFIS].[DASSA].[CORDICAR] c
    JOIN DEPOFIS.DASSA.[Clientes] cl ON c.cliente = cl.clie_nro
    WHERE c.tipo_oper = 'IMPORTACION' 
    AND c.fecha > '{fecha_ant1}'
""")   
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
arribos = pd.DataFrame.from_records(rows, columns=columns)

#Descargo EXPO a arribar
cursor.execute(f"""
    SELECT c.orden, c.contenedor, c.buque, c.terminal, c.fecha, c.turno, c.peso, c.operacion, c.arribado, 
            c.chapa_trac, c.bookings, c.tipo_oper, cl.apellido AS cliente, c.desc_merc, c.precinto, c.dimension
    FROM [DEPOFIS].[DASSA].[CORDICAR] c JOIN DEPOFIS.DASSA.[Clientes] cl ON c.cliente = cl.clie_nro 
    WHERE c.tipo_oper != 'IMPORTACION' AND c.fecha >= '{fecha_ant1}'
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
arribos_expo = pd.DataFrame.from_records(rows, columns=columns)

#Descargo Contendores Ingresados
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, fecha_ing, tipo_oper, contenedor FROM DEPOFIS.DASSA.[Ingresadas En Stock]
    WHERE fecha_ing BETWEEN '{fecha_ant}' AND '{fecha}'
    AND tipo_oper = 'IMPORTACION'
    AND suborden= 0
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ingresos = pd.DataFrame.from_records(rows, columns=columns)

#%% Formateo y procesamiento de datos Arribos
print('Procesando datos')

def transformar(df):
    # Dimension
    df['dimension'] = pd.to_numeric(df['dimension'])
    df.loc[df['dimension'] == 20, 'dimension'] = 30
    df.loc[(df['dimension'] == 40) & (df['tipo_cnt'] == 'HC'), 'dimension'] = 70
    df.loc[(df['dimension'] == 40) & (df['tipo_cnt'] != 'HC'), 'dimension'] = 60
    df['dimension'] = df['dimension'].astype(int)
    df['dimension'] = df['dimension'].astype(str)
    # Terminal
    df['terminal'] = df['terminal'].astype(str)
    terminal_mapping = {
        '10057': 'TRP',
        '10073': 'Exolgan',
        '10068': 'Terminal 4'}
    df['terminal'] = df['terminal'].replace(terminal_mapping)
    # Contenedor
    df['contenedor'] = df['contenedor'].str.strip()
    df = df[df['contenedor'] != '']
    # Operacion
    df['operacion'] = df['operacion'].str.strip()
    return df

def crear_operacion(df): 
    df['operacion'] = (df['orden_ing'].astype(str) + '-' + df['suborden'].astype(str) + '-' + df['renglon'].astype(str))
    return(df)

# IMPO a arribar
arribos = transformar(arribos)
arribos['Turno2'] = arribos['turno'].str.strip().apply(lambda x: x[:2] + ":" + x[2:] + ":00" if x.strip() else pd.NaT)
arribos['Fecha y Hora'] = pd.to_datetime(arribos['fecha']) + pd.to_timedelta(arribos['Turno2'])
current_time = pd.Timestamp.now()
arribos['tiempo_transcurrido'] = current_time - arribos['Fecha y Hora']
arribos['tiempo_transcurrido'] = arribos['tiempo_transcurrido'].apply(lambda x: '-' if x.days < 0 else '{:02}:{:02}'.format(x.seconds // 3600, (x.seconds // 60) % 60))
arribos['cliente'] =  arribos['cliente'].str.title()
arribos['buque'] =  arribos['buque'].str.title()

# EXPO a arribar
arribos_expo['terminal'] = arribos_expo['terminal'].astype(str)
terminal_mapping = {
    '10057': 'TRP',
    '10073': 'Exolgan',
    '10068': 'Terminal 4'}
arribos_expo['terminal'] = arribos_expo['terminal'].replace(terminal_mapping)
arribos_expo['contenedor'] = arribos_expo['contenedor'].str.strip()
arribos_expo['operacion'] = arribos_expo['operacion'].str.strip()
arribos_expo['tipo_oper'] = arribos_expo['tipo_oper'].str.strip()
arribos_expo['cliente'] =  arribos_expo['cliente'].str.strip()
arribos_expo['cliente'] =  arribos_expo['cliente'].str.title()
arribos_expo['arribado'] = arribos_expo['arribado'].replace({0: 'Pendiente', 1: 'Arribado'})

arribos_expo_historico_horarios = pd.read_csv('arribos_expo_historico_horarios.csv')
arribos_expo = pd.merge(arribos_expo, arribos_expo_historico_horarios, on=['orden'], how='left')
arribos_expo['arribado'] = arribos_expo['estado'].fillna(arribos_expo['arribado'])
arribos_expo = arribos_expo.drop(columns=['estado'])

arribos_expo_carga = arribos_expo[arribos_expo['tipo_oper'] != 'VACIO']
arribos_expo_carga = arribos_expo_carga[['fecha', 'orden', 'contenedor' , 'cliente', 'bookings', 'desc_merc', 'arribado']]
arribos_expo_carga.columns = ['Fecha', 'Operacion', 'Contenedor', 'Cliente', 'Booking', 'Descripcion', 'Estado']
arribos_expo_carga['Descripcion'] = arribos_expo_carga['Descripcion'].str.strip()
arribos_expo_carga['Booking'] = arribos_expo_carga['Booking'].str.strip()

arribos_expo_ctns = arribos_expo[arribos_expo['tipo_oper'] == 'VACIO']
arribos_expo_ctns = arribos_expo_ctns[['fecha', 'orden', 'contenedor' , 'cliente', 'bookings', 'precinto', 'arribado']]
arribos_expo_ctns.columns = ['Fecha', 'Operacion', 'Contenedor', 'Cliente', 'Booking', 'Precinto', 'Estado']
arribos_expo_ctns['Booking'] = arribos_expo_ctns['Booking'].str.strip()

arribos_expo_carga.to_csv(os.path.join(path, 'data/arribos_expo_carga_historico.csv'), index=False)
arribos_expo_ctns.to_csv(os.path.join(path, 'data/arribos_expo_ctns_historico.csv'), index=False)


#Contenedores ingresados
ingresos['contenedor'] = ingresos['contenedor'].str.strip()
arribados = arribos[arribos['arribado']==1]

arribos = pd.merge(arribos, ingresos[['contenedor', 'fecha_ing']], on=['contenedor'], how='left')
arribos['Pendiente'] = arribos['fecha_ing'].isna().astype(int)

arribos = arribos[['fecha', 'turno', 'terminal', 'contenedor', 'cliente', 'bookings', 'operacion', 'fecha_ing']]
arribos.columns = ['Fecha', 'Turno', 'Terminal', 'Contenedor', 'Cliente', 'Booking', 'Operacion', 'Fecha Ingreso']
arribos['Cliente'] = arribos['Cliente'].str.strip()
arribos['Booking'] = arribos['Booking'].str.strip()
arribos['Turno'] = arribos['Turno'].str.strip().apply(lambda x: x[:2] + ":" + x[2:]  if x.strip() else pd.NaT)

arribos.to_csv(os.path.join(path, 'data/arribos_impo_historico.csv'), index=False)


# Turnos

def limpiar_columnas(df):
    columns = ['cliente', 'tipo_oper', 'desc_merc', 'Envase']
    for column in columns:
        if column in df.columns:
            df[column] = df[column].str.strip()
            df[column] = df[column].str.title()
    return df

fecha = datetime.now().strftime('%Y-%m-%d')
fecha_ant = datetime.now() - timedelta(days=120)
fecha_ant = fecha_ant.strftime('%Y-%m-%d')
fecha_ant_ult3dias = datetime.now() - timedelta(days=3)
fecha_ant_ult3dias = fecha_ant_ult3dias.strftime('%Y-%m-%d') 
cursor.execute("""
    SELECT e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing, 
    e.contenedor, e.conocim1, e.desc_merc, e.dimension, e.tipo_cnt, e.volumen, env.detalle AS Envase, 
    e.cantidad, e.conocim2, e.kilos, e.bookings, e.precinto
    FROM [DEPOFIS].[DASSA].[Existente en Stock] e
    JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
existente = pd.DataFrame.from_records(rows, columns=columns)
#Descargo Ubicaciones
#Ubicaciones del exisntente
cursor.execute("""
    SELECT orden_ing, suborden, renglon, ubicacion
    FROM [DEPOFIS].[DASSA].[Ubic_St]
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ubicaciones_existente = pd.DataFrame.from_records(rows, columns=columns)
#Ubicaciones del egresado
cursor.execute(f"""
SELECT  orden_ing, suborden, renglon, ubicacion
FROM [DEPOFIS].[DASSA].[Egresadas del stock]
WHERE fecha_egr > '{fecha_ant}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ubicaciones_egresado = pd.DataFrame.from_records(rows, columns=columns)
ubicaciones = pd.concat([ubicaciones_existente, ubicaciones_egresado], ignore_index=True)

#Egresado
cursor.execute(f"""
SELECT  e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing, 
e.contenedor, e.desc_merc, e.conocim AS conocim1, e.dimension, e.tipo_cnt, e.volumen, env.detalle AS Envase, e.fecha_egr, e.cantidad
FROM [DEPOFIS].[DASSA].[Egresadas del stock] e
JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
WHERE e.fecha_egr > '{fecha_ant}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
egresado = pd.DataFrame.from_records(rows, columns=columns)
egresado['cantidad'] *= -1
#Verificaciones realizadas
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, fechaverif            
    FROM [DEPOFIS].[DASSA].[Todo] 
    WHERE fechaverif > '{fecha_ant}'
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
verificaciones_realizadas = pd.DataFrame.from_records(rows, columns=columns)
#Salidas validadas
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, validada          
    FROM [DEPOFIS].[DASSA].[Salidas] 
    WHERE validada > '{fecha_ant}'
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
salidas = pd.DataFrame.from_records(rows, columns=columns)

#Turnos
cursor.execute(f"""
SELECT orden_ing, suborden, renglon, destino, dia, hora, observa, conocim2
FROM DEPOFIS.DASSA.[TURNOSSA] as e
WHERE dia >= '{fecha_ant}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
turnos = pd.DataFrame.from_records(rows, columns=columns)
turnos['destino'] = turnos['destino'].str.strip()
turnos['Estado'] = 'Pendiente'
turnos['observa'] = turnos['observa'].str.strip()
turnos = turnos[turnos['orden_ing'] != 0]

#Genero ids para hacer matcheos
def generate_id(df):
    df['id'] = df[['orden_ing', 'suborden', 'renglon']].astype(str).agg('-'.join, axis=1)
    df.drop(columns=['orden_ing', 'suborden', 'renglon'], inplace=True)
    return df

turnos['id'] = turnos[['orden_ing', 'suborden', 'renglon']].astype(str).agg('-'.join, axis=1)
existente['id'] = existente[['orden_ing', 'suborden', 'renglon']].astype(str).agg('-'.join, axis=1)
egresado = generate_id(egresado)
verificaciones_realizadas = generate_id(verificaciones_realizadas)
salidas = generate_id(salidas)
salidas.columns = ['salida_validada', 'id']
ubicaciones = generate_id(ubicaciones)
turnos = limpiar_columnas(turnos)
existente = limpiar_columnas(existente)

#Separo segun tipo de turnos
verificaciones = turnos[turnos['destino'].str.contains('Verificacion', case=False, na=False)]
consolidados = turnos[turnos['destino'].str.contains('Consolidado', case=False, na=False)]
retiros_remisiones = turnos[turnos['destino'].str.contains('Retiro|Remi', case=False, na=False)]

## 1. Consolidados
existente_a_consolidar = pd.merge(consolidados, existente.drop(columns=['id', 'suborden', 'renglon', 'conocim2']), on='orden_ing', how='inner')
contenedores_a_consolidar = existente_a_consolidar[existente_a_consolidar['Envase'] == 'Contenedor']
mercaderia_a_consolidar = existente_a_consolidar[existente_a_consolidar['Envase'] != 'Contenedor']
mercaderia_a_consolidar = mercaderia_a_consolidar.groupby('orden_ing').agg({
    'volumen': 'sum',
    'cantidad': 'sum',
    'kilos': 'sum'}).reset_index()

contenedores_a_consolidar.drop(columns=['volumen', 'cantidad', 'kilos'], inplace=True)
consolidados = pd.merge(contenedores_a_consolidar, mercaderia_a_consolidar, on='orden_ing', how='left')
consolidados['kilos'] = consolidados['kilos'].fillna(0).astype(float).round().astype(int)

# Quito conocimiento del existente
existente.drop(columns=['conocim2', 'orden_ing', 'suborden', 'renglon'], inplace=True)

## 2. Retiros y remisiones
retiros_remisiones_egr = pd.merge(retiros_remisiones, egresado, on='id', how='inner')
retiros_remisiones_egr['fecha_egr'] = pd.to_datetime(retiros_remisiones_egr['fecha_egr']).dt.date
retiros_remisiones_egr['Estado'] = 'Pendiente'
retiros_remisiones_egr['Estado'] = retiros_remisiones_egr.apply(
    lambda row: 'En curso' if row['fecha_egr'] == datetime.now().date() else row['Estado'],
    axis=1
)
retiros_remisiones_exist = pd.merge(retiros_remisiones, existente, on='id', how='inner')
retiros_remisiones_exist['Estado'] = 'Pendiente'
#retiros_remisiones_exist = retiros_remisiones_exist[~retiros_remisiones_exist['id'].isin(retiros_remisiones_egr['id'])]  #Se sacan casos de retiros parciales (VER QUE TODAVIA HAY PROBLEMAS)
retiros_remisiones_egr = retiros_remisiones_egr[~retiros_remisiones_egr['id'].isin(retiros_remisiones_exist['id'])]
retiros_remisiones = pd.concat([retiros_remisiones_egr, retiros_remisiones_exist], ignore_index=True)
retiros_remisiones = pd.merge(retiros_remisiones, salidas, on='id', how='left')
retiros_remisiones = pd.merge(retiros_remisiones, salidas_vacios, on='id', how='left')
retiros_remisiones['fecha_salida_validada'] = pd.to_datetime(retiros_remisiones['salida_validada'], errors='coerce').dt.date
retiros_remisiones['salida_validada'] = retiros_remisiones.apply(
    lambda row: float('nan') if pd.notna(row['fecha_salida_validada']) and row['fecha_salida_validada'] < datetime.now().date() else row['salida_validada'],
    axis=1)
retiros_remisiones.drop(columns=['fecha_salida_validada'], inplace=True)
retiros_remisiones['Estado'] = retiros_remisiones.apply(
    lambda row: row['salida_validada'][11:16] + ' Realizado' if pd.notna(row['salida_validada']) else row['Estado'],
    axis=1)

## 3. Verificaciones
verificaciones= pd.merge(verificaciones, verificaciones_realizadas, on='id', how='left')
verificaciones['Estado'] = verificaciones['fechaverif'].apply(lambda x: 'Realizado' if pd.notna(x) else 'Pendiente')
verificaciones_existente = pd.merge(verificaciones, existente, on='id', how='inner')
verificaciones_egresado = pd.merge(verificaciones, egresado, on='id', how='inner')
verificaciones_sin_dato = verificaciones[
    ~verificaciones['id'].isin(verificaciones_existente['id']) &
    ~verificaciones['id'].isin(verificaciones_egresado['id'])
]
verificaciones = pd.concat([verificaciones_existente, verificaciones_egresado, verificaciones_sin_dato], ignore_index=True)

## 4. Clasificaciones
clasificaciones = turnos[turnos['destino'].str.contains('Clasi', case=False, na=False)]
clasificaciones_existente = pd.merge(clasificaciones, existente, on='id', how='inner')
clasificaciones_egresado = pd.merge(clasificaciones, egresado, on='id', how='inner')
clasificaciones_sin_dato = clasificaciones[~clasificaciones['id'].isin(clasificaciones_existente['id']) & ~clasificaciones['id'].isin(clasificaciones_egresado['id'])]
clasificaciones = pd.concat([clasificaciones_existente, clasificaciones_egresado, clasificaciones_sin_dato], ignore_index=True)

#Junto verificaciones con resto de turnos
turnos = pd.concat([retiros_remisiones, verificaciones, consolidados, clasificaciones], ignore_index=True)
#Join de ubicaciones
turnos = pd.merge(turnos, ubicaciones, on='id', how='left')
turnos = limpiar_columnas(turnos)


## Parte que estaba en la app
turnos['volumen'] = turnos['volumen'].fillna(0).astype(float).round().astype(int)
turnos['kilos'] = turnos['kilos'].fillna(0).astype(float).round().astype(int)
turnos['cliente'] = turnos['cliente'].fillna('').apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
turnos['desc_merc'] = turnos['desc_merc'].fillna('').apply(lambda x: x[:20] + "..." if len(x) > 20 else x)
turnos['precinto'] = turnos['precinto'].fillna('---')
turnos['ubicacion'] = turnos['ubicacion'].str.strip()
turnos[['conocim1', 'conocim2']] = turnos[['conocim1', 'conocim2']].fillna('-')

verificaciones_expo = turnos[(turnos['tipo_oper'] == 'Exportacion') & (turnos['destino'] == 'Verificacion')]
verificaciones_expo = verificaciones_expo[['dia', 'cliente', 'desc_merc', 'bookings', 'contenedor', 'Envase', 'cantidad', 'volumen', 'ubicacion', 'Estado']]
verificaciones_expo = rellenar_df_vacio(verificaciones_expo)
verificaciones_expo.columns = ['Dia', 'Cliente', 'Desc. Merc.', 'Booking', 'Contenedor', 'Envase', 'Cantidad', 'Volumen', 'Ubic.', 'Estado']

verificaciones_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (turnos['destino'] == 'Verificacion')]
verificaciones_impo = verificaciones_impo[['dia', 'cliente', 'desc_merc', 'contenedor', 'Envase', 'cantidad', 'volumen', 'ubicacion', 'Estado']]
verificaciones_impo.columns = ['Dia', 'Cliente', 'Desc. Merc.', 'Contenedor', 'Envase', 'Cant.', 'Volumen', 'Ubic.', 'Estado']

retiros_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (turnos['destino'] == 'Retiro')]
retiros_impo = retiros_impo[['dia', 'cliente', 'conocim1', 'contenedor', 'Envase', 'cantidad', 'volumen','ubicacion', 'Estado']]
retiros_impo.columns = ['Dia', 'Cliente', 'Conocim.', 'Contenedor', 'Envase', 'Cant.', 'Volumen','Ubic.', 'Estado']
retiros_impo['Conocim.'] = retiros_impo['Conocim.'].str.strip()

otros_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (~turnos['destino'].isin(['Retiro', 'Verificacion']))]
otros_impo = otros_impo[['dia', 'hora', 'destino', 'id', 'cliente', 'contenedor', 'Envase', 'cantidad', 'volumen', 'ubicacion', 'Estado']]
otros_impo.columns = ['Dia', 'Hora', 'Tipo Turno', 'Operacion', 'Cliente', 'Contenedor', 'Envase', 'Cant.', 'Volumen', 'Ubic.', 'Estado']

retiros_expo = turnos[(turnos['tipo_oper'] == 'Exportacion') & (turnos['destino'] == 'Retiro')]
retiros_expo = retiros_expo[['dia', 'cliente', 'conocim1', 'contenedor', 'Envase', 'cantidad', 'ubicacion', 'Estado']]
retiros_expo.columns = ['Dia', 'Cliente', 'Conocim.', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.', 'Estado']

otros_expo = turnos[(turnos['tipo_oper'] == 'Exportacion') & (~turnos['destino'].isin(['Retiro', 'Verificacion', 'Remision', 'Consolidado']))]
otros_expo = otros_expo[['dia', 'hora', 'destino', 'id', 'cliente', 'contenedor', 'Envase', 'cantidad', 'ubicacion']]
otros_expo.columns = ['Dia', 'Hora', 'Tipo Turno', 'Operacion', 'Cliente', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.']

remisiones = turnos[(turnos['tipo_oper'] == 'Exportacion') & (turnos['destino'] == 'Remision')]
remisiones = remisiones[['dia', 'cliente', 'contenedor', 'volumen', 'precinto', 'observa', 'Estado']]
remisiones.columns = ['Dia', 'Cliente', 'Contenedor', 'Volumen', 'Precinto', 'Observaciones', 'Estado']

consolidados = turnos[turnos['destino'] == 'Consolidado']
consolidados = consolidados[['dia', 'cliente', 'contenedor', 'observa', 'volumen', 'cantidad', 'kilos']]
consolidados.columns = ['Dia', 'Cliente', 'Contenedor', 'Observaciones', 'Volumen', 'Cantidad', 'Kilos']

### PARCHE UNIQUES ###
verificaciones_expo = verificaciones_expo.drop_duplicates()
retiros_expo = retiros_expo.drop_duplicates()
retiros_impo = retiros_impo.drop_duplicates()
otros_expo = otros_expo.drop_duplicates()
remisiones = remisiones.drop_duplicates()
consolidados = consolidados.drop_duplicates()
clasificaciones = clasificaciones.drop_duplicates()
verificaciones_impo = verificaciones_impo.drop_duplicates()
otros_impo = otros_impo.drop_duplicates()

verificaciones_expo.to_csv(os.path.join(path, 'data/historico_verificaciones_expo.csv'), index=False)
verificaciones_impo.to_csv(os.path.join(path, 'data/historico_verificaciones_impo.csv'), index=False)
retiros_expo.to_csv(os.path.join(path, 'data/historico_retiros_expo.csv'), index=False)
retiros_impo.to_csv(os.path.join(path, 'data/historico_retiros_impo.csv'), index=False)
otros_expo.to_csv(os.path.join(path, 'data/historico_otros_expo.csv'), index=False)
otros_impo.to_csv(os.path.join(path, 'data/historico_otros_impo.csv'), index=False)
remisiones.to_csv(os.path.join(path, 'data/historico_remisiones.csv'), index=False)
consolidados.to_csv(os.path.join(path, 'data/historico_consolidados.csv'), index=False)

conn.close()

gc = gspread.service_account(filename='//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/credenciales_gsheets.json')
sheet_logs =  gc.open_by_url('https://docs.google.com/spreadsheets/d/1aPUkhige3tq7_HuJezTYA1Ko7BWZ4D4W0sZJtsTyq3A')                                           
worksheet_logs = sheet_logs.worksheet('Logeos')
df_logs = worksheet_logs.get_all_values()
df_logs = pd.DataFrame(df_logs[1:], columns=df_logs[0])
now = datetime.now().strftime('%Y-%m-%d %H:%M')
new_log_entry = pd.DataFrame([{'Rutina': 'Streamlit - Update Data Historico', 'Fecha y Hora': now}])
df_logs = pd.concat([df_logs, new_log_entry], ignore_index=True)
worksheet_logs.clear()
set_with_dataframe(worksheet_logs, df_logs)
print("Se registró el logeo")