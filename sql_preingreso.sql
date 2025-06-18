-- Table to store daily pre-ingreso records
CREATE TABLE preingreso (
    id SERIAL PRIMARY KEY,
    cliente_mercaderia TEXT NOT NULL,
    nombre_chofer TEXT NOT NULL,
    dni_chofer TEXT NOT NULL,
    patente_camion TEXT NOT NULL,
    patente_acoplado TEXT NOT NULL,
    celular_whatsapp TEXT NOT NULL,
    remito_permiso_embarque TEXT NOT NULL,
    tipo_carga TEXT NOT NULL,
    numero_fila INT NOT NULL,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table to store historical pre-ingreso records
CREATE TABLE preingreso_historico (
    id SERIAL PRIMARY KEY,
    cliente_mercaderia TEXT NOT NULL,
    nombre_chofer TEXT NOT NULL,
    dni_chofer TEXT NOT NULL,
    patente_camion TEXT NOT NULL,
    patente_acoplado TEXT NOT NULL,
    celular_whatsapp TEXT NOT NULL,
    remito_permiso_embarque TEXT NOT NULL,
    tipo_carga TEXT NOT NULL,
    numero_fila INT NOT NULL,
    fecha DATE NOT NULL,
    hora TIMESTAMP NOT NULL
);

-- Function to reset daily records and move them to the historical table
CREATE OR REPLACE FUNCTION reset_preingreso()
RETURNS VOID AS $$
BEGIN
    INSERT INTO preingreso_historico (cliente_mercaderia, nombre_chofer, dni_chofer, patente_camion, patente_acoplado, celular_whatsapp, remito_permiso_embarque, tipo_carga, numero_fila, fecha, hora)
    SELECT cliente_mercaderia, nombre_chofer, dni_chofer, patente_camion, patente_acoplado, celular_whatsapp, remito_permiso_embarque, tipo_carga, numero_fila, fecha, hora
    FROM preingreso;

    DELETE FROM preingreso;
END;
$$ LANGUAGE plpgsql;

-- Schedule the reset function to run daily at midnight
CREATE EXTENSION IF NOT EXISTS pg_cron;
SELECT cron.schedule('daily_reset_preingreso', '0 0 * * *', 'SELECT reset_preingreso();');
