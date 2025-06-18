import pyodbc
import pandas as pd
import os
from datetime import datetime
from tokens import username, password, password_gmail
from supabase_connection import fetch_table_data, delete_table_data, insert_table_data
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def update_log(table_name):
    log_entry = {
        "table_name": table_name,
        "last_update": datetime.now().isoformat()
    }
    supabase_client.from_("update_log").insert(log_entry).execute()

def send_email_report(preingreso_historico):
    today = datetime.now().strftime('%d/%m/%Y')
    email_content = f"""
    <html>
    <body>
        <h2>Reporte de Preingreso - {today}</h2>
        <p>Se ha realizado el reseteo diario de los registros de preingreso.</p>
        <h3>Registros movidos al histórico:</h3>
        {preingreso_historico.to_html(index=False, escape=False)}
        <p>Saludos cordiales,</p>
        <p><strong>Operativo DASSA</strong></p>
    </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['Subject'] = f'Reporte de Preingreso - {today}'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = "marajadesantelmo@gmail.com"
    msg.attach(MIMEText(email_content, 'html'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("auto@dassa.com.ar", password_gmail)
        server.sendmail(msg['From'], msg['To'], msg.as_string())

if os.path.exists('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/auto'):
    os.chdir('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/auto')
elif os.path.exists('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream/auto'):
    os.chdir('C:/Users/facun/OneDrive/Documentos/GitHub/dassa_operativo_stream/auto')
else:
    print("Se usa working directory por defecto")

print('Descargando datos de Preingreso')
preingreso_data = fetch_table_data("preingreso")

if not preingreso_data.empty:
    # Add timestamp columns
    preingreso_data['fecha'] = datetime.now().strftime('%Y-%m-%d')
    preingreso_data['hora'] = datetime.now().strftime('%H:%M:%S')

    print('Moviendo datos al histórico')
    insert_table_data("preingreso_historico", preingreso_data.to_dict(orient="records"))

    print('Reseteando tabla de Preingreso')
    delete_table_data("preingreso")

    print('Actualizando log')
    update_log("preingreso_historico")

    print('Enviando reporte por email')
    send_email_report(preingreso_data)
else:
    print("No hay datos en la tabla de Preingreso para mover.")
