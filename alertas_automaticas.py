import pandas as pd
import smtplib
from email.mime.text import MIMEText
arribos_impo = pd.read_csv('data/arribos2.csv')
historical_data = pd.read_csv('data/historical_alerts.csv')
arribados = arribos_impo[arribos_impo['Estado'] != 'Pendiente arribo']

if arribados.empty:
    print("No new arrivals. Exiting script.")
    exit()

arribos_con_historico = pd.merge(arribados, historical_data, on='Contenedor', how='left', suffixes=('', '_hist'))

alertas = arribos_con_historico[arribos_con_historico['alert_sent'].isna()]
     
# Function to send email
def send_email(alertas):
    msg = MIMEText(f"El contendedor {alertas['Contenedor']} del cliente {alertas['Cliente']} ")
    msg['Subject'] = 'Contenedor Arribado'
    msg['From'] = "auto@dassa.com.ar"
    msg['To'] = 'marajadesantelmo@gmail.com'

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls() 
        server.login("auto@dassa.com.ar", "gyctvgzuwfgvmlfu")
        server.sendmail(msg['From'], [msg['To']], msg.as_string())

# Send alerts for new status changes
for _, row in alertas.iterrows():
    send_email(row)

# Update historical data to mark alerts as sent
alertas['alert_sent'] = True
updated_historical_data = pd.concat([historical_data, alertas[['Contenedor', 'alert_sent']]])

# Save updated historical data
updated_historical_data.to_csv('data/historical_alerts.csv', index=False)

print("historical_alerts.csv has been created.")