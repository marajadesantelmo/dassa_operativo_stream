import numpy as np
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import os


def highlight(row):
    # Handle missing 'Estado' column or None values
    if 'Estado' not in row or pd.isna(row['Estado']) or row['Estado'] is None:
        return ['' for _ in row]
    estado = str(row['Estado'])  # Convert to string to handle any data type
    if "Realizado" in estado:
        return ['background-color: darkgreen; color: black' for _ in row]
    elif "En curso" in estado:
        return ['background-color: darkgoldenrod; color: black' for _ in row]
    elif 'Balanza' in row and 'Entrada' in str(row['Balanza']):
        return ['background-color: darkgoldenrod; color: black' for _ in row]
    elif "Arribado" in estado and row.get('Balanza', None) == "-":
        return ['background-color: darkgoldenrod; color: black' for _ in row]
    elif estado == "Vacio":
        return ['background-color: #b71c1c; color: black' for _ in row]
    elif "Arribado" in estado:
        return ['background-color: darkgreen; color: black' for _ in row]
    elif "Ingresado" in estado:
        return ['background-color: darkgreen; color: black' for _ in row]
    elif estado == "Pendiente ingreso":
        return ['background-color: darkgoldenrod; color: black' for _ in row]
    elif estado == "En Espera":
        return ['background-color: #444444; color: black' for _ in row]
    elif "anterior" in estado:
        return ['background-color: #b71c1c; color: black' for _ in row]
    else:
        return ['' for _ in row]

def rellenar_df_vacio(df):
    if df.empty:
        df = pd.DataFrame([['-'] * len(df.columns)], columns=df.columns)
    return df


def filter_dataframe_by_clients(df, allowed_clients):
    if allowed_clients is None:
        return df  # No filtering needed
    if 'Cliente' in df.columns:
        return  df[df['Cliente'].isin(allowed_clients)]
    if 'Razon Social' in df.columns:
        return df[df['Razon Social'].isin(allowed_clients)]

def generar_comprobante(balanza_row):
    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf = FPDF()
    pdf.add_page()
    
    # Check if membrete image exists
    membrete_path = "membrete.png"
    if not os.path.exists(membrete_path):
        # Create a placeholder or handle missing image
        print(f"Warning: {membrete_path} not found, continuing without header image")
    else:
        pdf.image(membrete_path, x=10, y=10, w=pdf.w - 20)
    
    # Add invoice title
    pdf.set_font("Arial", style='B', size=22)
    pdf.set_text_color(190, 30, 45)  # #be1e2d color
    pdf.ln(25)
    pdf.cell(200, 10, txt="Comprobante de pesaje en balanza    ", ln=True, align="R")
    pdf.ln(1)
    
    # Add id pesada, date and other fix text
    pdf.set_font("Arial", style='B', size=16)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(100, 6, txt=f"ID Pesada: {balanza_row.get('ID Pesada', '-')}", ln=False, align="L")
    pdf.cell(100, 6, txt=f"Fecha: {current_date}      ", ln=True, align="R")
    pdf.ln(5)
    
    # Add fixed data
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(0, 0, 0)  # Black border
    pdf.set_fill_color(211, 211, 211)  # Light gray background
    pdf.set_line_width(0.5)
    pdf.rect(x=10, y=pdf.get_y(), w=pdf.w - 20, h=20, style='D')  # Draw rectangle

    pdf.set_xy(15, pdf.get_y() + 2)  # Adjust position inside the rectangle
    pdf.cell(200, 6, txt="Certificado Habilitación: 307-45317        Balanza: Balanza de Camiones", ln=True, align="L")
    pdf.set_xy(15, pdf.get_y())
    pdf.cell(200, 6, txt="Vto. Certificación: 29/01/2026               Tipo: Camiones", ln=True, align="L")
    pdf.set_xy(15, pdf.get_y())
    pdf.cell(200, 6, txt="Aduana: 001                                            Lote Balanza: 11002", ln=True, align="L")
    pdf.ln(5)
    
    # Add table title
    pdf.set_font("Arial", style='B', size=12)
    pdf.set_text_color(131, 148, 150)  # Solarized base0 color
    pdf.cell(200, 10, txt="Detalles de operación en Balanza", ln=True, align="L")
    pdf.ln(3)

    # Add table rows
    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.set_font("Arial", size=10)
    left_fields = ['Cliente', 'CUIT Cliente', 'Entrada', 'Contenedor', 'Patente Chasis', 'Chofer' , 'Precinto', 'Observaciones' ]
    right_fields = ['ATA', 'CUIT ATA',  'Salida', 'Descripción', 'Patente Semi',  'Tipo Doc', 'DNI', 'Booking', 'Permiso Emb.']

    for left_field, right_field in zip(left_fields, right_fields):
        pdf.set_font("Arial", style='B', size=10)
        pdf.cell(35, 6, txt=f"{left_field}:", align="L")
        pdf.set_font("Arial", size=10)
        pdf.cell(55, 6, txt=str(balanza_row.get(left_field, '-')), align="C")
        pdf.set_font("Arial", style='B', size=10)
        pdf.cell(35, 6, txt=f"{right_field}:", align="L")
        pdf.set_font("Arial", size=10)
        pdf.cell(55, 6, txt=str(balanza_row.get(right_field, '-')), align="C")
        pdf.ln()

    # If there are remaining fields in right_fields
    if len(right_fields) > len(left_fields):
        for right_field in right_fields[len(left_fields):]:
            pdf.set_font("Arial", style='B', size=10)
            pdf.cell(35, 6, txt="", align="L")
            pdf.cell(55, 6, txt="", align="C")
            pdf.cell(35, 6, txt=f"{right_field}:", align="L")
            pdf.set_font("Arial", size=10)
            pdf.cell(55, 6, txt=str(balanza_row.get(right_field, '-')), align="C")
            pdf.ln()
    pdf.ln(2)

    # Add table title for weights
    pdf.set_font("Arial", style='B', size=12)
    pdf.set_text_color(0, 0, 0)  # Solarized base0 color
    pdf.cell(0, 10, txt="Pesaje en Balanza", ln=True, align="C")
    pdf.ln(3)

    # Add table rows for weights
    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.set_font("Arial", size=10)
    weight_fields = ['Peso Bruto', 'Peso Tara', 'Peso Neto', 'Tara CNT', 'Peso Mercadería']

    pdf.set_fill_color(211, 211, 211)  # Light gray background
    table_width = 100  # Total width of the table (50 + 50)
    start_x = (pdf.w - table_width) / 2  # Calculate starting x position to center the table

    for field in weight_fields:
        pdf.set_x(start_x)  # Set x position to start_x to center the table
        pdf.cell(50, 8, txt=str(field), border=1, align="C", fill=True)
        pdf.cell(50, 8, txt=str(balanza_row.get(field, '-')), border=1, align="C", fill=True)
        pdf.ln()
    pdf.ln(15)

    pdf.set_text_color(0, 0, 0)  # Reset to black
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 6, txt=" ........................                  ..............................                ..............................               .............................", ln=True, align="C")
    pdf.cell(200, 3, txt="Administración                      Encargado                      Transporte                                   Aduana", ln=True, align="C")
    pdf.cell(200, 6, txt="                                                                                                                                Leg.: .............................", ln=True, align="C")
    pdf.cell(200, 6, txt=" ........................                  ..............................                ..............................               .............................", ln=True, align="C")
    pdf.cell(200, 3, txt="Aclaración                          Aclaración                     Aclaración                                   Aclaración", ln=True, align="C")
    pdf.ln(15)
    pdf.set_font("Arial", style='B', size=10)
    pdf.set_text_color(190, 30, 45)   # Solarized base0 color
    pdf.cell(200, 3, txt="DASSA - Depósito Avellaneda Sur S.A.", ln=True, align="L")
    pdf.ln(2)
    pdf.set_font("Arial", size=8)
    pdf.set_text_color(131, 148, 150)  # Solarized base0 color
    pdf.multi_cell(0, 3, txt=(
        "Av. Crisólogo Larralde 3065, Sarandí,\n"
        "Avellaneda, Buenos Aires, Argentina\n"
        "Email: info@dassa.com.ar \n"
        "Teléfono: + 54 11 2206 9300"
    ), align="L")
    pdf.ln(5)

    # Return the PDF object instead of saving
    return pdf