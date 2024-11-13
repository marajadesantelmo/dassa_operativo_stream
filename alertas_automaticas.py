import pandas as pd
import smtplib
from email.mime.text import MIMEText
import re

arribados = pd.read_csv('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/alertas_arribos.csv')

alertas = arribados[arribados['alerta_enviada'] == 0]

if alertas.empty:
    print("No hay alertas para enviar")
    exit()

#clientes = pd.read_csv('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/contactos_clientes.csv')
#clientes['email'] = clientes['email'].str.replace(';', ',')
#def add_space_after_comma(email):
#    return re.sub(r',(?=\S)', ', ', email)
#clientes['email'] = clientes['email'].apply(add_space_after_comma)
#clientes['email'] = clientes['email'].str.replace('"', '')

# Function to send email
def send_email(alertas, mails):
    msg = MIMEText(f"El contendedor {alertas['Contenedor']} del cliente {alertas['Cliente']} ")
    msg['Subject'] = 'Contenedor Arribado'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = mails

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls() 
        server.login("auto@dassa.com.ar", "gyctvgzuwfgvmlfu")
        server.sendmail(msg['From'], [msg['To']], msg.as_string())

for _, row in alertas.iterrows():
    mails = clientes[clientes['clie_nro'] == row['Cliente']]['email'].values[0]
    send_email(row)

alertas['alerta_enviada'] = 1
arribados = arribados[arribados['alerta_enviada'] == 1]
arribados = pd.concat([arribados, alertas])

arribados.to_csv('//dc01/Usuarios/PowerBI/flastra/Documents/dassa_operativo_stream/arribos_historico_horarios.csv', index=False)
