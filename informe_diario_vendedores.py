import pandas as pd
import pyodbc
from datetime import datetime
from tokens import username, password, password_gmail 
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

def send_email_vendedor(row, mail, url=None):
    manana = (datetime.now() + timedelta(days=1)).strftime('%d/%m/%Y')
    if url is not None:
        email_content = f"""
        <html>
        <body>
            <h2>Operaciones para el día {manana}/h2>
            <p>Buenas tardes,</p>
            <p>A continación te compartimos las operacio</p>
            <p>Saludos cordiales,</p>
            <p><strong>Alertas automáticas - Dassa Operativo</strong></p>
            <img src="https://dassa.com.ar/wp-content/uploads/elementor/thumbs/DASSA-LOGO-3.0-2024-PNG-TRANSPARENTE-qrm2px9hpjbdymy2y0xddhecbpvpa9htf30ikzgxds.png" alt="Dassa Logo" width="200">
        </body>
        </html>
        """
    msg = MIMEMultipart()
    msg['Subject'] = f'Operaciones de tus clientes para el día de mañana {manana}'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = mail
    #msg['To'] = 'marajadesantelmo@gmail.com'
    msg.attach(MIMEText(email_content, 'html'))
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login("auto@dassa.com.ar", password_gmail)
        server.sendmail(msg['From'], msg['To'], msg.as_string())



server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()

print('Clientes Global comex')
cursor.execute(f"""
SELECT  apellido AS Cliente, clie_nro, vendedor
FROM DEPOFIS.DASSA.[Clientes]
""") 
rows = cursor.fetchall()
columns = [column[0] for column in cursor.description]
clientes= pd.DataFrame.from_records(rows, columns=columns)

clientes['Cliente'] = clientes['Cliente'].str.strip().str.title()
clientes['Cliente'] = clientes['Cliente'].apply(lambda x: x[:20] + "..." if len(x) > 20 else x)

dic_vendedores = pd.read_excel('diccionario_vendedores_puros_dassa.xlsx')

verificaciones_impo = pd.read_csv('data/verificaciones_impo.csv')
retiros_impo = pd.read_csv('data/retiros_impo.csv')
otros_impo = pd.read_csv('data/otros_impo.csv')

verificaciones_expo = pd.read_csv('data/verificaciones_expo.csv')
remisiones_expo = pd.read_csv('data/remisiones.csv')
consolidados_expo = pd.read_csv('data/consolidados.csv')
otros_expo = pd.read_csv('data/otros_expo.csv')

vendedores = dic_vendedores['nombre_vendedor'].unique()

for vendedor in vendedores:
    tabla_vendedor = dic_vendedores[dic_vendedores['nombre_vendedor'] == vendedor]
    vendedor_ids = tabla_vendedor['cod_vendedor'].unique()
    clientes_vendedor = clientes[clientes['vendedor'].isin(vendedor_ids)]['Cliente'].unique()
    dia = (datetime.now() + timedelta(days=1)).strftime('%d/%m')
    verificaciones_impo_vendedor = verificaciones_impo[verificaciones_impo['Cliente'].isin(clientes_vendedor)]
    retiros_impo_vendedor = retiros_impo[(retiros_impo['Cliente'].isin(clientes_vendedor)) & (retiros_impo['Dia'] == dia)]
    otros_impo_vendedor = otros_impo[otros_impo['Cliente'].isin(clientes_vendedor)]
    verificaciones_expo_vendedor = verificaciones_expo[verificaciones_expo['Cliente'].isin(clientes_vendedor)]
    remisiones_expo_vendedor = remisiones_expo[remisiones_expo['Cliente'].isin(clientes_vendedor)]
    consolidados_expo_vendedor = consolidados_expo[consolidados_expo['Cliente'].isin(clientes_vendedor)]
    otros_expo_vendedor = otros_expo[otros_expo['Cliente'].isin(clientes_vendedor)]


