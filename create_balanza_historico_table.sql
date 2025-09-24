-- SQL statement to create balanza_historico table in Supabase
-- This table stores historical balance data from historico_balanza.csv
CREATE TABLE balanza_historico (
    id SERIAL PRIMARY KEY,
    "ID Pesada" TEXT,
    "Cliente" TEXT,
    "CUIT Cliente" TEXT,
    "ATA" TEXT,
    "CUIT ATA" TEXT,
    "Contenedor" TEXT,
    "Entrada" TEXT,
    "Salida" TEXT,
    "Peso Bruto" NUMERIC,
    "Peso Tara" NUMERIC,
    "Peso Neto" NUMERIC,
    "Peso Mercadería" NUMERIC,
    "Tara CNT" NUMERIC,
    "Descripción" TEXT,
    "Patente Chasis" TEXT,
    "Patente Semi" TEXT,
    "Chofer" TEXT,
    "Tipo Doc" TEXT,
    "DNI" TEXT,
    "Observaciones" TEXT,
    "tipo_oper" TEXT,
    "Booking" TEXT,
    "Permiso Emb." TEXT,
    "Precinto" TEXT,
    "Fecha" DATE,
    "Estado" TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance on common queries
CREATE INDEX idx_balanza_historico_fecha ON balanza_historico(fecha);
CREATE INDEX idx_balanza_historico_id_pesada ON balanza_historico(id_pesada);
CREATE INDEX idx_balanza_historico_cliente ON balanza_historico(cliente);
CREATE INDEX idx_balanza_historico_contenedor ON balanza_historico(contenedor);
CREATE INDEX idx_balanza_historico_tipo_oper ON balanza_historico(tipo_oper);
CREATE INDEX idx_balanza_historico_estado ON balanza_historico(estado);

-- Create a function to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at on row updates
CREATE TRIGGER update_balanza_historico_updated_at 
    BEFORE UPDATE ON balanza_historico 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Add RLS (Row Level Security) if needed
-- ALTER TABLE balanza_historico ENABLE ROW LEVEL SECURITY;

-- Grant permissions (adjust according to your needs)
-- GRANT ALL ON balanza_historico TO authenticated;
-- GRANT ALL ON balanza_historico TO service_role;