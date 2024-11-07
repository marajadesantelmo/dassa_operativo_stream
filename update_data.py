'''
Script que actualiza los csv
'''



import pyodbc
import pandas as pd
import os
from datetime import datetime, timedelta
from email.message import EmailMessage
from datetime import datetime, timedelta
from tokens import username, password
from utils import rellenar_df_vacio

if os.path.exists('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_streamlit'):
    os.chdir('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_streamlit')
elif os.path.exists('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_streamlit'):
    os.chdir('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_streamlit')
else:
    print("Se usa working directory por defecto")

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

#Descargo contenedores IMPO a arribar
cursor.execute(f"""
    SELECT c.contenedor, c.buque, c.terminal, c.fecha, c.turno, c.peso, c.operacion, 
           c.arribado, c.dimension, c.tipo_cnt, c.despachant, c.precinto, c.bookings, 
           cl.apellido AS cliente
    FROM [DEPOFIS].[DASSA].[CORDICAR] c
    JOIN DEPOFIS.DASSA.[Clientes] cl ON c.cliente = cl.clie_nro
    WHERE c.tipo_oper = 'IMPORTACION' 
    AND c.fecha = '{fecha}'
""")   
           
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
arribos = pd.DataFrame.from_records(rows, columns=columns)

#Descargo EXPO a arribar
cursor.execute(f"""
SELECT c.orden, c.contenedor, c.buque, c.terminal, c.fecha, c.turno, c.peso, 
       c.operacion, c.arribado, c.chapa_trac, c.bookings,  c.tipo_oper, 
       cl.apellido AS cliente, c.desc_merc, c.precinto, c.dimension, c.hora_ing
FROM [DEPOFIS].[DASSA].[CORDICAR] c
JOIN DEPOFIS.DASSA.[Clientes] cl ON c.cliente = cl.clie_nro
WHERE c.tipo_oper != 'IMPORTACION' 
AND c.fecha >= '{fecha}'
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

#Descargo Contendores Desconsolidados
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, contenedor, fecha_ing, tipo_oper 
    FROM DEPOFIS.DASSA.[Ingresadas En Stock]
    WHERE fecha_ing BETWEEN '{fecha_ant}' AND '{fecha}'
    AND tipo_oper = 'IMPORTACION'
    AND suborden!= 0
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
desconsolidados = pd.DataFrame.from_records(rows, columns=columns)

#Descargo Contendores Consolidados
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, contenedor 
    FROM DEPOFIS.DASSA.[Ingresadas En Stock]
    WHERE fecha_ing BETWEEN '{fecha_ant}' AND '{fecha}'
    AND tipo_oper = 'EXPORTACION'
    AND suborden != 0 
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
consolidados = pd.DataFrame.from_records(rows, columns=columns)

###### Descargo listos para remitir
cursor.execute("""
 SELECT orden_ing, contenedor, conocim, cliente, bookings, tipo_cnt, dimension, fecha_ing 
 FROM DEPOFIS.DASSA.[Existente En Stock]
 WHERE tipo_oper = 'EXPORTACION'
 AND tipo_trans != 'MERCADERIA'
 AND suborden = 0    
""")  # Agregar filtro de consolidoados

rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
contenedores_existente_expo = pd.DataFrame.from_records(rows, columns=columns)


cursor.execute(f"""
    SELECT e.orden_ing, e.suborden, e.renglon, e.contenedor, e.fecha_ing, e.tipo_oper, 
           e.vto_vacio, e.cliente, e.cantidad, env.detalle AS Envase
    FROM DEPOFIS.DASSA.[Existente En Stock] e
    JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
    WHERE e.fecha_ing BETWEEN '{fecha_ant}' AND '{fecha}'
    AND e.tipo_oper = 'IMPORTACION'
    AND e.suborden = 0
""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
contenedores_existente_impo = pd.DataFrame.from_records(rows, columns=columns)

#Pendiente consolidar
cursor.execute("""
    SELECT orden_ing, suborden, renglon, contenedor, fecha_ing, tipo_oper, bookings, cantidad, kilos, volumen, cliente 
    FROM DEPOFIS.DASSA.[Existente En Stock]
    WHERE tipo_oper = 'EXPORTACION'
    AND tipo_trans = 'MERCADERIA'
    AND suborden = 0
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
pendiente_consolidar = pd.DataFrame.from_records(rows, columns=columns)

#Descargo contenedores IMPO a arribar y a desconsolidar en los ultimos dias
cursor.execute(f"""
    SELECT 
        c.contenedor, c.buque, c.terminal, c.fecha, c.turno, c.peso, 
        c.operacion, c.arribado, c.dimension, c.tipo_cnt, c.vto_vacio, 
        d.detalle AS Entrega
    FROM [DEPOFIS].[DASSA].[CORDICAR] c
    LEFT JOIN [DEPOFIS].[DASSA].[destinos] d ON c.term_ent = d.codigo
    WHERE c.tipo_oper = 'IMPORTACION' 
    AND c.fecha BETWEEN '{fecha_ant}' AND '{fecha}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
arribados_a_desconsolidar = pd.DataFrame.from_records(rows, columns=columns)

#Descargo Existente IMPO
cursor.execute("""
    SELECT orden_ing, suborden, renglon, cliente, agencia, fecha_ing, contenedor, conocim1, desc_merc, dimension, tipo_cnt, volumen, kilos
    FROM [DEPOFIS].[DASSA].[Existente en Stock]
    WHERE tipo_oper = 'IMPORTACION' 
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
existente_impo = pd.DataFrame.from_records(rows, columns=columns)

#Descargo Ubicaciones IMPO
cursor.execute("""
    SELECT orden_ing, suborden, renglon, ubicacion
    FROM [DEPOFIS].[DASSA].[Ubic_St]
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ubicaciones_existente = pd.DataFrame.from_records(rows, columns=columns)

#Egresado 
cursor.execute(f"""
SELECT  e.orden_ing, e.suborden, e.renglon, e.cliente, e.tipo_oper, e.fecha_ing, 
e.contenedor, e.desc_merc, e.conocim AS conocim1, e.dimension, e.tipo_cnt, e.volumen, env.detalle AS Envase
FROM [DEPOFIS].[DASSA].[Egresadas del stock] e
JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
WHERE e.fecha_egr > '{fecha_ant}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
egresado = pd.DataFrame.from_records(rows, columns=columns)
egresado['id'] = egresado[['orden_ing', 'suborden', 'renglon']].astype(str).agg('-'.join, axis=1)


#Tally
cursor.execute("""
    SELECT t.tally, cl.apellido AS Cliente, bookings, contenedor, cantidad, kilos, volumen, dimension, env.detalle AS Envase
    FROM [DEPOFIS].[DASSA].[Tally] t
    JOIN DEPOFIS.DASSA.[Clientes] cl ON t.cliente = cl.clie_nro
    JOIN DEPOFIS.DASSA.[Tip_env] env ON t.tipo_env = env.codigo""")
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
tally = pd.DataFrame.from_records(rows, columns=columns)
tally = tally.tail(100)

#%% Formateo y procesamiento de datos Arribos
print('Procesando datos de arribos')

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
arribos_expo['Contenedor2'] = arribos_expo['contenedor'].str.strip()    # Ver para que contenedor2
arribos_expo['cliente'] =  arribos_expo['cliente'].str.title()
arribos_expo['Estado'] = arribos_expo['arribado'].replace({0: 'Pendiente', 1: 'Arribado'})
arribos_expo.loc[arribos_expo['Estado'] == 'Arribado', 'Estado'] = arribos_expo['hora_ing'].astype(str) + ' Arribado'

#Contenedores ingresados
ingresos['contenedor'] = ingresos['contenedor'].str.strip()
arribados = arribos[arribos['arribado']==1]
pendiente_ingresado=  arribados[~arribados['contenedor'].isin(ingresos['contenedor'])]
arribados_a_desconsolidar = transformar(arribados_a_desconsolidar)

#Pendientes desconsolidar y vacios
egresado['tipo_oper'] = egresado['tipo_oper'].str.strip()
egresado['contenedor'] = egresado['contenedor'].str.strip()
desco_egresados = egresado[(egresado['suborden'] == 0) & (egresado['tipo_oper'] == 'IMPORTACION')]
desco_egresados = desco_egresados[desco_egresados['contenedor']!=""]
desco_egresados = desco_egresados['contenedor'].unique()
contenedores_existente_impo['contenedor'] = contenedores_existente_impo['contenedor'].str.strip()
contenedores_existente_impo= contenedores_existente_impo[contenedores_existente_impo['contenedor'] != '']
arribados_a_desconsolidar= arribados_a_desconsolidar[arribados_a_desconsolidar['operacion'] == 'TD']
arribados_a_desconsolidar= arribados_a_desconsolidar[arribados_a_desconsolidar['arribado'] == 1]
arribados_a_desconsolidar['Entrega'] = arribados_a_desconsolidar['Entrega'].str.title()
desconsolidados = desconsolidados['contenedor'].unique()
pendiente_desconsolidar = arribados_a_desconsolidar[arribados_a_desconsolidar['contenedor']!=""]
pendiente_desconsolidar['Estado'] = 'Pte. Desc.'
pendiente_desconsolidar.loc[pendiente_desconsolidar['contenedor'].isin(desconsolidados), 'Estado'] = 'Vacio'
pendiente_desconsolidar = pendiente_desconsolidar[~pendiente_desconsolidar.isin(desco_egresados)]
contenedores_existente = contenedores_existente_impo['contenedor'].unique()
pendiente_desconsolidar = pendiente_desconsolidar[pendiente_desconsolidar['contenedor'].isin(contenedores_existente)]
pendiente_desconsolidar = pendiente_desconsolidar.merge(
    contenedores_existente_impo[['contenedor', 'cliente', 'cantidad']],
    on='contenedor',
    how='left'
)
pendiente_desconsolidar['cliente'] = pendiente_desconsolidar['cliente'].str.title()
pendiente_desconsolidar.drop(columns=['cantidad'], inplace=True)
# Group by 'contenedor' and aggregate the required columns
tally_resumen= tally.groupby('contenedor').agg({
    'cantidad': 'sum',
    'kilos': 'sum',
    'Envase': lambda x: ', '.join(x.unique())
}).reset_index()
tally_resumen['Envase'] = tally_resumen['Envase'].str.title()
pendiente_desconsolidar = pendiente_desconsolidar.merge(tally_resumen, on='contenedor', how='left')

##Existente EXPO##
#Pendiente de consolidar
pendiente_consolidar['contenedor'] = pendiente_consolidar['contenedor'].str.strip()
pendiente_consolidar['cliente'] = pendiente_consolidar['cliente'].str.strip()
pendiente_consolidar['cliente'] = pendiente_consolidar['cliente'].str.title()
fecha_actual = datetime.strptime(fecha, '%Y-%m-%d')
pendiente_consolidar['fecha_ing'] = pd.to_datetime(pendiente_consolidar['fecha_ing'], format='%Y-%m-%d')
pendiente_consolidar['Dias'] = (fecha_actual - pendiente_consolidar['fecha_ing']).dt.days

#Pendiente de remitir
consolidados['contenedor'] = consolidados['contenedor'].str.strip()
consolidados = consolidados['contenedor'].unique()
listos_para_remitir = contenedores_existente_expo[contenedores_existente_expo['contenedor'].isin(consolidados)]
vacios_disponibles = contenedores_existente_expo[~contenedores_existente_expo['contenedor'].isin(consolidados)]
vacios_disponibles['cliente'] = vacios_disponibles['cliente'].str.title()
listos_para_remitir['cliente'] = listos_para_remitir['cliente'].str.title()

listos_para_remitir['fecha_ing'] = pd.to_datetime(listos_para_remitir['fecha_ing'], format='%Y-%m-%d')
listos_para_remitir['Dias'] = (fecha_actual - listos_para_remitir['fecha_ing']).dt.days

#Existente IMPO
existente_impo['contenedor'] = existente_impo['contenedor'].str.strip()
existente_impo = crear_operacion(existente_impo)
ubicaciones_existente = crear_operacion(ubicaciones_existente)
ubicaciones_existente['ubicacion'] = ubicaciones_existente['ubicacion'].str.strip()
existente_impo = pd.merge(existente_impo, ubicaciones_existente[['operacion', 'ubicacion']], on='operacion', how='left')
familias_ubicaciones = pd.read_excel('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/flias_ubicaciones.xlsx')
existente_impo = pd.merge(existente_impo, familias_ubicaciones[['ubicacion', 'ubicacion_familia']], on='ubicacion', how='left')
existente_impo['teus'] = existente_impo['dimension']/20
existente_plz = existente_impo[existente_impo['ubicacion_familia'].isin(['Plazoleta', 'Temporal'])]
existente_alm = existente_impo[~existente_impo['ubicacion_familia'].isin(['Plazoleta', 'Temporal'])]

# Creo variable estado en Arribos IMPO
arribos['Estado'] = arribos['arribado'].apply(lambda x: 'Pendiente arribo' if x == 0 else 'Arribado')
arribos.loc[arribos['contenedor'].isin(pendiente_ingresado['contenedor']), 'Estado'] = 'Pendiente ingreso'
arribos.loc[arribos['Estado'] == 'Arribado', 'tiempo_transcurrido'] = '---'

arribos_historico_horarios = pd.read_csv('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/arribos_historico_horarios.csv')
arribos = pd.merge(arribos, arribos_historico_horarios[['contenedor', 'fecha', 'estado']], on=['contenedor', 'fecha'], how='left')
arribos['Estado'] = arribos['estado'].fillna(arribos['Estado'])
arribos = arribos.drop(columns=['estado'])

arribos_recientes = arribos[arribos['Estado']=='Arribado']
arribos_recientes['estado'] = datetime.now().strftime('%H:%M') + ' Arribado' 
arribos_recientes = arribos_recientes[['fecha', 'contenedor', 'estado']]
arribos_historico_horarios = pd.concat([arribos_historico_horarios, arribos_recientes], ignore_index=True)
arribos_historico_horarios.to_csv('arribos_historico_horarios.csv', index=False)


## Parte que estaba en la app

arribos_expo_carga = arribos_expo[arribos_expo['tipo_oper'] != 'VACIO']
arribos_expo_ctns = arribos_expo[arribos_expo['tipo_oper'] == 'VACIO']
arribos_expo_carga = arribos_expo_carga[['fecha', 'bookings', 'cliente', 'desc_merc', 'Estado']]
arribos_expo_carga.columns = ['Fecha', 'Bookings', 'Cliente', 'Desc. Merc.', 'Estado']
arribos_expo_ctns = arribos_expo_ctns[['fecha', 'bookings', 'cliente', 'dimension', 'contenedor', 'precinto','Estado']]
arribos_expo_ctns.columns = ['Fecha', 'Bookings', 'Cliente', 'Dimension', 'Contenedor', 'Precinto', 'Estado']   

arribos = arribos[['terminal', 'turno', 'contenedor', 'cliente', 'bookings', 'tipo_cnt', 'tiempo_transcurrido', 'Estado']]
arribos.columns = ['Terminal', 'Turno', 'Contenedor', 'Cliente', 'Bookings', 'Tipo', 'Temp.', 'Estado']
arribos['Cliente'] = arribos['Cliente'].apply(lambda x: x[:10] + "..." if len(x) > 10 else x)
arribos['Bookings'] = arribos['Bookings'].apply(lambda x: x[:10] + "..." if len(x) > 10 else x)
arribos['Turno'] = arribos['Turno'].apply(lambda x: f"{str(x)[:-2]}:{str(x)[-2:]}")

pendiente_desconsolidar = pendiente_desconsolidar[['contenedor', 'cliente', 'Entrega', 'vto_vacio', 'tipo_cnt', 'peso','Estado']]
pendiente_desconsolidar.columns = ['Contenedor', 'Cliente', 'Entrega', 'Vto. Vacio', 'Tipo', 'Peso', 'Estado']
pendiente_desconsolidar['Entrega'] = pendiente_desconsolidar['Entrega'].fillna('-')
pendiente_desconsolidar['Cliente'] = pendiente_desconsolidar['Cliente'].apply(lambda x: x[:10] + "..." if len(x) > 10 else x)

arribos = rellenar_df_vacio(arribos)
pendiente_desconsolidar = rellenar_df_vacio(pendiente_desconsolidar)

arribos.to_csv('data/arribos.csv', index=False)
arribos_expo_carga.to_csv('data/arribos_expo_carga.csv', index=False)
arribos_expo_ctns.to_csv('data/arribos_expo_ctns.csv', index=False)
pendiente_ingresado.to_csv('data/pendiente_ingresado.csv', index=False)
pendiente_desconsolidar.to_csv('data/pendiente_desconsolidar.csv', index=False)
pendiente_consolidar.to_csv('data/pendiente_consolidar.csv', index=False)
listos_para_remitir.to_csv('data/listos_para_remitir.csv', index=False)
vacios_disponibles.to_csv('data/vacios_disponibles.csv', index=False)
existente_plz.to_csv('data/existente_plz.csv', index=False)
existente_alm.to_csv('data/existente_alm.csv', index=False)    


#### TURNOS ####
print('Procesando datos de Turnos')

def limpiar_columnas(df):
    columns = ['cliente', 'tipo_oper', 'desc_merc', 'Envase']
    for column in columns:
        if column in df.columns:
            df[column] = df[column].str.strip()
            df[column] = df[column].str.title()
    return df

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
#Existente
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
e.contenedor, e.desc_merc, e.conocim AS conocim1, e.dimension, e.tipo_cnt, e.volumen, env.detalle AS Envase, e.fecha_egr, e.cantidad, e.bookings
FROM [DEPOFIS].[DASSA].[Egresadas del stock] e
JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
WHERE e.fecha_egr > '{fecha_ant}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
egresado = pd.DataFrame.from_records(rows, columns=columns)
egresado['cantidad'] *= -1
egresado['volumen'] *= -1
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
#Salidas vacios validadas
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, validada          
    FROM [DEPOFIS].[DASSA].[Vacios] 
    WHERE validada > '{fecha_ant}'
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
salidas_vacios = pd.DataFrame.from_records(rows, columns=columns)
#Turnos
cursor.execute(f"""
SELECT orden_ing, suborden, renglon, destino, dia, hora, observa, conocim2
FROM DEPOFIS.DASSA.[TURNOSSA] as e
WHERE dia >= '{fecha}'
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
turnos = pd.DataFrame.from_records(rows, columns=columns)
turnos['destino'] = turnos['destino'].str.strip()
turnos['Estado'] = 'Pendiente'
turnos['observa'] = turnos['observa'].str.strip()
turnos = turnos[turnos['orden_ing'] != 0]

conn.close()


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
salidas_vacios = generate_id(salidas_vacios)
salidas_vacios.columns = ['salida_vacio_validada', 'id']
ubicaciones = generate_id(ubicaciones)

turnos = limpiar_columnas(turnos)
existente = limpiar_columnas(existente)
#Separo segun tipo de turnos
verificaciones = turnos[turnos['destino'].str.contains('Verificacion', case=False, na=False)]
consolidados = turnos[turnos['destino'].str.contains('Consolidado', case=False, na=False)]
turnos = turnos[turnos['destino'].str.contains('Retiro|Remi', case=False, na=False)]

# Consolidados
existente_a_consolidar = pd.merge(consolidados, existente.drop(columns=['id', 'suborden', 'renglon', 'conocim2']), on='orden_ing', how='inner')
contenedores_a_consolidar = existente_a_consolidar[existente_a_consolidar['Envase'] == 'Contenedor']
mercaderia_a_consolidar = existente_a_consolidar[existente_a_consolidar['Envase'] != 'Contenedor']
mercaderia_a_consolidar = mercaderia_a_consolidar.groupby('orden_ing').agg({
    'volumen': 'sum',
    'cantidad': 'sum',
    'kilos': 'sum'}).reset_index()

# Join de contenedores y mercaderia
contenedores_a_consolidar.drop(columns=['volumen', 'cantidad', 'kilos'], inplace=True)

consolidados = pd.merge(contenedores_a_consolidar, mercaderia_a_consolidar, on='orden_ing', how='left')


# Quito conocimiento del existente
existente.drop(columns=['conocim2', 'orden_ing', 'suborden', 'renglon'], inplace=True)

# Retiros y remisiones (lo trato a parte porque tengo que hacer match con salidas)
turnos_egr = pd.merge(turnos, egresado, on='id', how='inner')
turnos_egr['Estado'] = 'En curso'
turnos_exist = pd.merge(turnos, existente, on='id', how='inner')
turnos_exist['Estado'] = 'Pendiente'
turnos_exist = turnos_exist[~turnos_exist['id'].isin(turnos_egr['id'])] #Se sacan casos de retiros parciales
turnos = pd.concat([turnos_egr, turnos_exist], ignore_index=True)
turnos = pd.merge(turnos, salidas, on='id', how='left')
turnos = pd.merge(turnos, salidas_vacios, on='id', how='left')
turnos['fecha_salida_validada'] = pd.to_datetime(turnos['salida_validada'], errors='coerce').dt.date
turnos['salida_validada'] = turnos.apply(
    lambda row: float('nan') if pd.notna(row['fecha_salida_validada']) and row['fecha_salida_validada'] < datetime.now().date() else row['salida_validada'],
    axis=1)
turnos.drop(columns=['fecha_salida_validada'], inplace=True)
turnos['Estado'] = turnos.apply(
    lambda row: row['salida_validada'][11:16] + ' Realizado' if pd.notna(row['salida_validada']) else row['Estado'],
    axis=1)

# Verificaciones
verificaciones= pd.merge(verificaciones, verificaciones_realizadas, on='id', how='left')
verificaciones['Estado'] = verificaciones['fechaverif'].apply(lambda x: 'Realizado' if pd.notna(x) else 'Pendiente')
verificaciones_existente = pd.merge(verificaciones, existente, on='id', how='inner')
verificaciones_egresado = pd.merge(verificaciones, egresado, on='id', how='inner')
# Verificaciones sin dato
verificaciones_sin_dato = verificaciones[
    ~verificaciones['id'].isin(verificaciones_existente['id']) &
    ~verificaciones['id'].isin(verificaciones_egresado['id'])
]
verificaciones = pd.concat([verificaciones_existente, verificaciones_egresado, verificaciones_sin_dato], ignore_index=True)
#Junto verificaciones con resto de turnos
turnos = pd.concat([turnos, verificaciones, consolidados], ignore_index=True)
#Join de ubicaciones
turnos = pd.merge(turnos, ubicaciones, on='id', how='left')
turnos = limpiar_columnas(turnos)



## Parte que estaba en la app

turnos['cliente'] = turnos['cliente'].apply(lambda x: x[:10] + "..." if len(x) > 10 else x)
turnos['desc_merc'] = turnos['desc_merc'].apply(lambda x: x[:10] + "..." if len(x) > 10 else x)
turnos['ubicacion'] = turnos['ubicacion'].str.strip()

verificaciones_expo = turnos[(turnos['tipo_oper'] == 'Exportacion') & (turnos['destino'] == 'Verificacion')]
verificaciones_expo = verificaciones_expo[['dia', 'cliente', 'desc_merc', 'contenedor', 'Envase', 'cantidad', 'ubicacion']]
verificaciones_expo = rellenar_df_vacio(verificaciones_expo)
verificaciones_expo.columns = ['Dia', 'Cliente', 'Desc. Merc.', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.']

verificaciones_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (turnos['destino'] == 'Verificacion')]
verificaciones_impo = verificaciones_impo[['dia', 'cliente', 'desc_merc', 'contenedor', 'Envase', 'cantidad', 'ubicacion', 'Estado']]
verificaciones_impo.columns = ['Dia', 'Cliente', 'Desc. Merc.', 'Contenedor', 'Envase', 'Cant.', 'Ubic.', 'Estado']

retiros_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (turnos['destino'] == 'Retiro')]
retiros_impo = retiros_impo[['dia', 'cliente', 'conocim1', 'contenedor', 'Envase', 'cantidad', 'ubicacion', 'Estado']]
retiros_impo.columns = ['Dia', 'Cliente', 'Conocim.', 'Contenedor', 'Envase', 'Cant.', 'Ubic.', 'Estado']
retiros_impo['Conocim.'] = retiros_impo['Conocim.'].str.strip()

otros_impo = turnos[(turnos['tipo_oper'] == 'Importacion') & (~turnos['destino'].isin(['Retiro', 'Verificacion']))]
otros_impo = otros_impo[['dia', 'hora', 'id', 'cliente', 'contenedor', 'Envase', 'cantidad', 'ubicacion', 'Estado']]
otros_impo.columns = ['Dia', 'Hora', 'Operacion', 'Cliente', 'Contenedor', 'Envase', 'Cant.', 'Ubic.', 'Estado']


retiros_expo = turnos[(turnos['tipo_oper'] == 'Exportacion') & (turnos['destino'] == 'Retiro')]
retiros_expo = retiros_expo[['dia', 'cliente', 'conocim1', 'contenedor', 'Envase', 'cantidad', 'ubicacion', 'Estado']]
retiros_expo.columns = ['Dia', 'Cliente', 'Conocim.', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.', 'Estado']

otros_expo = turnos[(turnos['tipo_oper'] == 'Exportacion') & (~turnos['destino'].isin(['Retiro', 'Verificacion']))]
otros_expo = otros_expo[['dia', 'hora', 'id', 'cliente', 'contenedor', 'Envase', 'cantidad', 'ubicacion']]
otros_expo.columns = ['Dia', 'Hora', 'Operacion', 'Cliente', 'Contenedor', 'Envase', 'Cantidad', 'Ubic.']

remisiones = turnos[turnos['destino'] == 'Remision']
consolidados = turnos[turnos['destino'] == 'Consolidado']

verificaciones_expo = rellenar_df_vacio(verificaciones_expo)
retiros_expo = rellenar_df_vacio(retiros_expo)
retiros_impo = rellenar_df_vacio(retiros_impo)
otros_expo = rellenar_df_vacio(otros_expo)
remisiones = rellenar_df_vacio(remisiones)
consolidados = rellenar_df_vacio(consolidados)

verificaciones_impo = rellenar_df_vacio(verificaciones_impo)
otros_impo = rellenar_df_vacio(otros_impo)


verificaciones_expo.to_csv('data/verificaciones_expo.csv', index=False)
verificaciones_impo.to_csv('data/verificaciones_impo.csv', index=False)
retiros_expo.to_csv('data/retiros_expo.csv', index=False)
retiros_impo.to_csv('data/retiros_impo.csv', index=False)
otros_expo.to_csv('data/otros_expo.csv', index=False)
otros_impo.to_csv('data/otros_impo.csv', index=False)
remisiones.to_csv('data/remisiones.csv', index=False)
consolidados.to_csv('data/consolidados.csv', index=False)
