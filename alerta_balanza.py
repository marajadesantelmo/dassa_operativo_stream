import pandas as pd
import pyodbc
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

alertas_balanza = pd.read_csv('alertas_balanza.csv')

clientes = pd.read_csv('contactos_clientes.csv')
clientes['email'] = clientes['email'].str.replace(';', ',')
clientes['email'] = clientes['email'].str.replace('"', '')
clientes['email'] = clientes['email'].apply(lambda x: [email.strip() for email in x.split(',')])

alertas_balanza = pd.read_csv('alertas_balanza.csv')
alertas_balanza_a_enviar = alertas_balanza[alertas_balanza['enviado'] == 0]
alertas_balanza_enviadas = alertas_balanza[alertas_balanza['enviado'] == 1]

today = pd.Timestamp.today().strftime('%Y-%m-%d')

conn = pyodbc.connect('DRIVER={SQL Server};SERVER=101.44.8.58\\SQLEXPRESS_X86,1436;UID=dassa;PWD=Da$$a3065!')
cursor = conn.cursor()

#BALANZA
cursor.execute(f"""
SELECT idpesada, idcliente, cl_nombre, idata, ata_nombre, entrada, salida, peso_bruto, peso_tara, peso_neto, contenedor
FROM DEPOFIS.DASSA.BALANZA_PESADA
WHERE fecha > '2025-01-15'
""")

rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
balanza = pd.DataFrame.from_records(rows, columns=columns)

balanza['cl_nombre'] = balanza['cl_nombre'].str.strip().str.title()
balanza['ata_nombre'] = balanza['ata_nombre'].str.strip().str.title()

balanza.to_csv('ver_balanza.csv', index=False)


#CONTENEDORES IMPO INGRESADOS EN STOCK
cursor.execute(f"""
    SELECT orden_ing, suborden, renglon, contenedor, fecha_ing, tipo_oper 
    FROM DEPOFIS.DASSA.[Ingresadas En Stock]
    WHERE fecha_ing > '2025-01-15'
    AND tipo_oper = 'IMPORTACION'
    AND suborden= 0
""")  
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
cnts_ingresados = pd.DataFrame.from_records(rows, columns=columns)

cnts_ingresados.to_csv('ver_contenedores_ingresados.csv', index=False)


# Filtrar EXPO y salida
def send_email(row, mail):
    # Get the current time
    current_time = datetime.now().strftime('%H:%M')
    email_content = f"""
    <html>
    <body>
        <h2>Notificación de Pesada</h2>
        <p>Estimado cliente,</p>
        <p>Le informamos que el contenedor <strong>{row['contenedor']}</strong> del cliente <strong>{row['cliente']}</strong> arribó a las instalaciones de DASSA a las <strong>{current_time}</strong>.</p>
        <p>Saludos cordiales,</p>
        <p><strong>Alertas automáticas - Dassa Operativo</strong></p>
        <img src="https://dassa.com.ar/wp-content/uploads/elementor/thumbs/DASSA-LOGO-3.0-2024-PNG-TRANSPARENTE-qrm2px9hpjbdymy2y0xddhecbpvpa9htf30ikzgxds.png" alt="Dassa Logo" width="200">
    </body>
    </html>
    """
    msg = MIMEMultipart()
    msg['Subject'] = 'Notificación de Contenedor Arribado'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = "marajadesantelmo@gmail.com"
    msg.attach(MIMEText(email_content, 'html'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("auto@dassa.com.ar", "gyctvgzuwfgvmlfu")
        server.sendmail(msg['From'], msg['To'], msg.as_string())