-- Create table for Plazoleta stock data
CREATE TABLE IF NOT EXISTS control_stock_existente_plz (
    id BIGSERIAL PRIMARY KEY,
    "Cliente" TEXT,
    "Cantidad" INTEGER,
    "Peso" NUMERIC(10, 2),
    "Volumen" NUMERIC(10, 2),
    "Tipo" TEXT,
    "Envase" TEXT,
    "Ingreso" DATE,
    "Operacion" TEXT,
    "Ubicacion" TEXT,
    "Ubicacion Familia" TEXT,
    "Dias" INTEGER,
    "Estiba OK" TEXT,
    "Alcahuete OK" TEXT,
    "Observaciones" TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create table for Almacen stock data
CREATE TABLE IF NOT EXISTS control_stock_existente_alm (
    id BIGSERIAL PRIMARY KEY,
    "Cliente" TEXT,
    "Cantidad" INTEGER,
    "Peso" NUMERIC(10, 2),
    "Volumen" NUMERIC(10, 2),
    "Tipo" TEXT,
    "Envase" TEXT,
    "Ingreso" DATE,
    "Operacion" TEXT,
    "Ubicacion" TEXT,
    "Ubicacion Familia" TEXT,
    "Dias" INTEGER,
    "Estiba OK" TEXT,
    "Alcahuete OK" TEXT,
    "Observaciones" TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security (RLS) if needed
ALTER TABLE control_stock_existente_plz ENABLE ROW LEVEL SECURITY;
ALTER TABLE control_stock_existente_alm ENABLE ROW LEVEL SECURITY;

-- Create policies to allow read access (adjust as needed for your security requirements)
CREATE POLICY "Enable read access for all users" ON control_stock_existente_plz
    FOR SELECT USING (true);

CREATE POLICY "Enable read access for all users" ON control_stock_existente_alm
    FOR SELECT USING (true);

-- Create policies to allow insert/update/delete for authenticated users (adjust as needed)
CREATE POLICY "Enable insert for authenticated users" ON control_stock_existente_plz
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users" ON control_stock_existente_plz
    FOR UPDATE USING (true);

CREATE POLICY "Enable delete for authenticated users" ON control_stock_existente_plz
    FOR DELETE USING (true);

CREATE POLICY "Enable insert for authenticated users" ON control_stock_existente_alm
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users" ON control_stock_existente_alm
    FOR UPDATE USING (true);

CREATE POLICY "Enable delete for authenticated users" ON control_stock_existente_alm
    FOR DELETE USING (true);
