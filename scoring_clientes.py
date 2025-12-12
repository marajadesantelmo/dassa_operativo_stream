




print('Descargando datos de SQL')
import pyodbc
from datetime import datetime, timedelta
server = '101.44.8.58\\SQLEXPRESS_X86,1436'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+ password)
cursor = conn.cursor()
fecha_ant = datetime.now() - timedelta(days=7)
fecha_ant= fecha_ant.strftime('%Y-%m-%d')