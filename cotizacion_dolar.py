

## Scraping de BCRA
import subprocess
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

#Ejecutar el archivo por lotes (.bat) para abrir mozilla
try:
    subprocess.Popen(['activar_mozilla.bat'])
    print("Navegador abierto exitosamente.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred while executing the batch file: {e}")

time.sleep(2)
service = Service(executable_path="C:/Users/facun/OneDrive/Documentos/GitHub/scraping_linkedin/geckodriver.exe", port=3000, service_args=['--marionette-port', '2828', '--connect-existing'])
driver = webdriver.Firefox(service=service)
# Volver a la primera ventana
driver.switch_to.window(driver.window_handles[0])
driver.get('https://www.bcra.gob.ar/PublicacionesEstadisticas/Planilla_cierre_de_cotizaciones.asp?moneda=2')

soup = BeautifulSoup(driver.page_source, 'html.parser')
table = soup.find('table')
data = []
rows = table.find_all('tr')


data = []

# Iterar sobre las filas de la tabla (saltando las filas del encabezado)
for row in table.find_all('tr')[2:]:  # Skip the first two header rows
    cols = row.find_all('td')  # Encontrar todas las columnas
    if len(cols) > 0:
        fecha = cols[0].text.strip()
        comprador = cols[1].text.strip()
        vendedor = cols[2].text.strip()
        data.append([fecha, comprador, vendedor])
df_bcra = pd.DataFrame(data, columns=['Fecha', 'Comprador', 'Vendedor'])

# Guardar el DataFrame de BCRA en un archivo Excel


df_bcra = pd.read_excel('bcra_data.xlsx')
df_bcra['Comprador'] = df_bcra['Comprador'].str.replace('.', '').str.replace(',', '.').astype(float)
df_bcra['Vendedor'] = df_bcra['Vendedor'].str.replace('.', '').str.replace(',', '.').astype(float)
#Interpolación de valores faltantes
df_bcra['Fecha'] = pd.to_datetime(df_bcra['Fecha'], format='%d-%m-%Y', dayfirst=True)
df_bcra.set_index('Fecha', inplace=True)
full_index = pd.date_range(start=df_bcra.index.min(), end=df_bcra.index.max())
df_bcra = df_bcra.reindex(full_index).interpolate()
df_bcra.reset_index(inplace=True)
df_bcra.rename(columns={'index': 'Fecha'}, inplace=True)
df_bcra['Fecha'] = df_bcra['Fecha'].dt.strftime('%d-%m-%Y')
df_bcra.to_excel('bcra_data.xlsx', index=False)



### Procesamiento de datos bajados de dolar hoy

import pandas as pd
dolar_blue = pd.read_csv(r'cotizacion_dolar_bue.csv')
#Interpolacion de valores faltantes
dolar_blue['category'] = pd.to_datetime(dolar_blue['category'])
dolar_blue.set_index('category', inplace=True)
full_index = pd.date_range(start=dolar_blue.index.min(), end=dolar_blue.index.max())
dolar_blue = dolar_blue.reindex(full_index).interpolate()
dolar_blue.reset_index(inplace=True)
dolar_blue.rename(columns={'index': 'category'}, inplace=True)

dolar_blue.to_excel(r'cotizacion_dolar_bue.xlsx', index=False)