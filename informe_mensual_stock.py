"""Script que genera el informe mensual de stock existente en DASSA y lo sube a Supabase.
Además, envía un correo de notificación a los responsables.
"""


import pandas as pd
import pyodbc
from datetime import datetime
from tokens import username, password, password_gmail 
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import gspread
from gspread_dataframe import set_with_dataframe
from tokens import username, password, url_supabase, key_supabase
from supabase import create_client, Client

supabase_client = create_client(url_supabase, key_supabase)

path = "//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/"

server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

#gc = gspread.service_account(filename='//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/credenciales_gsheets.json')

cursor.execute("""
    SELECT cliente AS Cliente, cantidad AS Cantidad, kilos AS Peso, volumen AS Volumen, conocim AS Booking, contenedor AS Contenedor,
            orden_ing, suborden, renglon, tipo_oper AS Tipo, env.detalle AS Envase, fecha_ing AS Ingreso
    FROM [DEPOFIS].[DASSA].[Existente en Stock] e
    JOIN DEPOFIS.DASSA.[Tip_env] env ON e.tipo_env = env.codigo
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
existente = pd.DataFrame.from_records(rows, columns=columns)

cursor.execute("""
    SELECT orden_ing, suborden, renglon, ubicacion
    FROM [DEPOFIS].[DASSA].[Ubic_St]
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
ubicaciones_existente = pd.DataFrame.from_records(rows, columns=columns)

def crear_operacion(df): 
    df['Operacion'] = (df['orden_ing'].astype(str) + '-' + df['suborden'].astype(str) + '-' + df['renglon'].astype(str))
    df.drop(columns=['orden_ing', 'suborden', 'renglon'], inplace=True)
    return(df)

ubicaciones_existente = crear_operacion(ubicaciones_existente)
existente = crear_operacion(existente)
ubicaciones_existente['ubicacion'] = ubicaciones_existente['ubicacion'].str.strip()
existente = pd.merge(existente, ubicaciones_existente[['Operacion', 'ubicacion']], on='Operacion', how='left')
familias_ubicaciones = pd.read_excel('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/flias_ubicaciones.xlsx')
existente = pd.merge(existente, familias_ubicaciones[['ubicacion', 'ubicacion_familia']], on='ubicacion', how='left')
fecha_actual = datetime.now()
existente['Ingreso'] = pd.to_datetime(existente['Ingreso'], format='%Y-%m-%d')
existente['Dias'] = (fecha_actual - existente['Ingreso']).dt.days

cols = ['Cliente', 'Tipo', 'Envase']
for col in cols:
    existente[col] = existente[col].str.strip().str.title()

existente.rename(columns={'ubicacion': 'Ubicacion', 'ubicacion_familia': 'Ubicacion Familia'}, inplace=True)

existente = existente[['Ubicacion Familia', 'Ubicacion', 'Cliente', 'Booking', 'Contenedor', 'Tipo', 'Envase', 'Peso', 'Volumen',  'Cantidad', 'Ingreso',
       'Operacion',  'Dias']]

existente['Estiba OK'] = ""
existente['Alcahuete OK'] = ""
existente['Observaciones'] = ""

existente.sort_values(by=['Ubicacion Familia', 'Ubicacion'], inplace=True)

existente_plz = existente[existente['Ubicacion Familia'].isin(['Plazoleta', 'Temporal'])].copy()
existente_alm = existente[~existente['Ubicacion Familia'].isin(['Plazoleta', 'Temporal'])].copy()

existente_alm.drop(columns=['Contenedor'], inplace=True)

#sheet = gc.create('Control_Stock_DASSA_{mes}_{year}'.format(mes=datetime.now().strftime('%m'), year=datetime.now().year))
#sheet.share('marajadesantelmo@gmail.com', perm_type='user', role='writer')
#sheet.share('santiago@dassa.com.ar', perm_type='user', role='writer')
#sheet.share('manuel@dassa.com.ar', perm_type='user', role='writer')
#worksheet_plz = sheet.add_worksheet(title='Plazoleta', rows=existente_plz.shape[0] + 10, cols=existente_plz.shape[1] + 5)
#set_with_dataframe(worksheet_plz, existente_plz, include_index=False)
#worksheet_alm = sheet.add_worksheet(title='Almacen', rows=existente_alm.shape[0] + 10, cols=existente_alm.shape[1] + 5)
#set_with_dataframe(worksheet_alm, existente_alm, include_index=False)
#default_worksheet = sheet.get_worksheet(0)
#sheet.del_worksheet(default_worksheet)

#print(f"Spreadsheet created: {sheet.url}")

# Upload to Supabase
def upload_to_supabase(df, table_name):
    """Delete all data from table and insert new data"""
    try:
        # Delete all existing data
        print(f"Deleting existing data from {table_name}...")
        supabase_client.from_(table_name).delete().neq('id', 0).execute()
        
        # Prepare data for insertion
        # Convert DataFrame to list of dictionaries and handle data types
        df_copy = df.copy()
        
        # Keep original column names (do NOT rename to lowercase)
        # Convert datetime columns to string format
        if 'Ingreso' in df_copy.columns:
            df_copy['Ingreso'] = pd.to_datetime(df_copy['Ingreso']).dt.strftime('%Y-%m-%d')
        
        # Convert Decimal types to appropriate numeric types for JSON serialization
        from decimal import Decimal
        
        # Handle numeric columns - convert Decimals but preserve integer types
        if 'Cantidad' in df_copy.columns:
            df_copy['Cantidad'] = df_copy['Cantidad'].apply(
                lambda x: int(x) if isinstance(x, (Decimal, float, int)) and pd.notna(x) else None
            )
        
        if 'Dias' in df_copy.columns:
            df_copy['Dias'] = df_copy['Dias'].apply(
                lambda x: int(x) if isinstance(x, (Decimal, float, int)) and pd.notna(x) else None
            )
        
        # Handle float columns - convert Decimals to float
        float_columns = ['Peso', 'Volumen']
        for col in float_columns:
            if col in df_copy.columns:
                df_copy[col] = df_copy[col].apply(
                    lambda x: float(x) if isinstance(x, (Decimal, float, int)) and pd.notna(x) else None
                )
        
        # Handle remaining object columns that might contain Decimals
        for col in df_copy.columns:
            if df_copy[col].dtype == 'object' and col not in ['Ingreso']:
                # Check if column contains Decimal objects
                if df_copy[col].apply(lambda x: isinstance(x, Decimal)).any():
                    df_copy[col] = df_copy[col].apply(lambda x: float(x) if isinstance(x, Decimal) else x)
        
        # Replace NaN values with None
        df_copy = df_copy.where(pd.notna(df_copy), None)
        
        # Convert to records
        records = df_copy.to_dict('records')
        
        # Additional cleanup: ensure all Decimal values are converted and integers are proper ints
        for record in records:
            for key, value in record.items():
                if isinstance(value, Decimal):
                    if key in ['Cantidad', 'Dias']:
                        record[key] = int(value)
                    else:
                        record[key] = float(value)
                elif isinstance(value, float) and key in ['Cantidad', 'Dias']:
                    # Ensure integer fields are actually integers
                    record[key] = int(value) if value is not None else None
        
        # Insert data in batches to avoid timeouts
        batch_size = 100
        total_records = len(records)
        
        print(f"Inserting {total_records} records into {table_name}...")
        for i in range(0, total_records, batch_size):
            batch = records[i:i + batch_size]
            supabase_client.from_(table_name).insert(batch).execute()
            print(f"Inserted batch {i//batch_size + 1}/{(total_records + batch_size - 1)//batch_size}")
        
        print(f"Successfully uploaded {total_records} records to {table_name}")
        
    except Exception as e:
        print(f"Error uploading to {table_name}: {e}")
        raise e

# Upload data to Supabase tables

# Fetch data from supabase and save it as excel file with previous month name
def fetch_data_and_save_excel():
    # Get the previous month name
    previous_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%B_%Y')
    # Fetch data from Supabase
    data_plz = supabase_client.from_('control_stock_existente_plz').select('*').execute()
    data_alm = supabase_client.from_('control_stock_existente_alm').select('*').execute()
    df_plz = pd.DataFrame(data_plz.data)
    df_alm = pd.DataFrame(data_alm.data)
    # Save to Excel
    df_plz.to_excel(os.path.join(path, 'data_stock', f'control_stock_existente_plz_{previous_month}.xlsx'), index=False)
    df_alm.to_excel(os.path.join(path, 'data_stock', f'control_stock_existente_alm_{previous_month}.xlsx'), index=False)

fetch_data_and_save_excel()

print("\n--- Starting Supabase upload ---")
supabase_client.from_('control_stock_existente_plz').delete().neq('id', 0).execute()
upload_to_supabase(existente_plz, 'control_stock_existente_plz')
supabase_client.from_('control_stock_existente_alm').delete().neq('id', 0).execute()
upload_to_supabase(existente_alm, 'control_stock_existente_alm')
print("--- Supabase upload completed ---\n")





def send_email(mail):
    """Send notification email about stock control availability"""
    current_time = datetime.now().strftime('%H:%M')
    current_month = datetime.now().strftime('%B %Y')
    
    email_content = f"""
    <html>
    <body>
        <p>Estimado,</p>
        
        <p>Ya se encuentra disponible la información actualizada para realizar el control de stock del mes corriente en <a href="https://dassa.tech/control_stock">dassa.tech/control_stock</a></p>
        
        <p>El informe fue generado el {datetime.now().strftime('%d/%m/%Y')} a las {current_time} y contiene:</p>
        <ul>
            <li>Stock en Plazoleta: {len(existente_plz):,} registros</li>
            <li>Stock en Almacén: {len(existente_alm):,} registros</li>
        </ul>
        
        <p>Saludos cordiales,<br>
        <strong>Sistema Automatizado DASSA</strong></p>
    </body>
    </html>
    """
    
    msg = MIMEMultipart()
    msg['Subject'] = f'DASSA • Control de Stock - Información Actualizada'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = mail
    msg.attach(MIMEText(email_content, 'html'))
    
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login("auto@dassa.com.ar", "gyctvgzuwfgvmlfu")
            server.sendmail(msg['From'], msg['To'], msg.as_string())
        print(f"Email sent successfully to {mail}")
    except Exception as e:
        print(f"Error sending email to {mail}: {e}")

# Send notification emails
print("--- Sending notification emails ---")
recipients = [
    "santiago@dassa.com.ar",
    "manuel@dassa.com.ar", 
    "marajadesantelmo@gmail.com", 
    "alan@dassa.com.ar"
]

for email in recipients:
    send_email(email)
