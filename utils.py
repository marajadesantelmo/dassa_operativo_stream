import numpy as np
import pandas as pd
from datetime import datetime
from fpdf import FPDF


def highlight(row):
    if "Realizado" in row['Estado']:
        return ['background-color: darkgreen; color: black' for _ in row]
    elif "En curso" in row['Estado']:
        return ['background-color: darkgoldenrod; color: black' for _ in row]
    elif 'Balanza' in row and 'Entrada' in str(row['Balanza']):
        return ['background-color: darkgoldenrod; color: black' for _ in row]
    elif "Arribado" in row['Estado'] and row.get('Balanza', None) == "-":
        return ['background-color: darkgoldenrod; color: black' for _ in row]
    elif row['Estado'] == "Vacio":
        return ['background-color: #be1e2d; color: black' for _ in row]
    elif "Arribado" in row['Estado']:
        return ['background-color: darkgreen; color: black' for _ in row]
    elif row['Estado'] == "Pendiente ingreso":
        return ['background-color: darkgoldenrod; color: black' for _ in row]
    elif row['Estado'] == "En Espera":
        return ['background-color: #444444; color: black' for _ in row]
    elif "anterior" in row['Estado']:
        return ['background-color: #be1e2d; color: black' for _ in row]
    else:
        return ['' for _ in row]

def rellenar_df_vacio(df):
    if df.empty:
        df = pd.DataFrame([['-'] * len(df.columns)], columns=df.columns)
    return df

def generar_comprobante(balanza_row):
    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf = FPDF()
    pdf.add_page()
    pdf.image("membrete.png", x=10, y=10, w=pdf.w - 20)
    # Add invoice title
    pdf.set_font("Arial", style='B', size=22)
    pdf.set_text_color(190, 30, 45)  # #be1e2d color
    pdf.ln(25)
    pdf.cell(200, 10, txt="Comprobante de pesaje en balanza    ", ln=True, align="R")
    pdf.ln(1)
    # Add id pesada, date and other fix text
    pdf.set_font("Arial", style='B', size=16)
    pdf.set_text_color(0, 0, 0)  
    pdf.cell(100, 6, txt=f"ID Pesada: {balanza_row['ID Pesada']}", ln=False, align="L")
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
        pdf.cell(55, 6, txt=str(balanza_row[left_field]), align="C")
        pdf.set_font("Arial", style='B', size=10)
        pdf.cell(35, 6, txt=f"{right_field}:", align="L")
        pdf.set_font("Arial", size=10)
        pdf.cell(55, 6, txt=str(balanza_row[right_field]), align="C")
        pdf.ln()

    # If there are remaining fields in right_fields
    if len(right_fields) > len(left_fields):
        for right_field in right_fields[len(left_fields):]:
            pdf.set_font("Arial", style='B', size=10)
            pdf.cell(35, 6, txt="", align="L")
            pdf.cell(55, 6, txt="", align="C")
            pdf.cell(35, 6, txt=f"{right_field}:", align="L")
            pdf.set_font("Arial", size=10)
            pdf.cell(55, 6, txt=str(balanza_row[right_field]), align="C")
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
        pdf.cell(50, 8, txt=str(balanza_row[field]), border=1, align="C", fill=True)
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

    # Save the PDF and return it
    pdf_output = f"comprobante_{balanza_row['ID Pesada']}.pdf"
    pdf.output(pdf_output)
    return pdf