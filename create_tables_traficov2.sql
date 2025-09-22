-- SQL statements to create Traffic Management v2 tables in Supabase
-- These tables will store synchronized data from the existing operational tables

-- Table for storing arribos data (IMPO arrivals)
CREATE TABLE IF NOT EXISTS traficov2_arribos (
    id SERIAL PRIMARY KEY,
    "Terminal" TEXT,
    "Turno" TEXT,
    "Contenedor" TEXT,
    "Cliente" TEXT,
    "Booking" TEXT,
    "Tipo CNT" TEXT,
    "Oper." TEXT,
    "Tiempo" TEXT,
    "Estado" TEXT,
    "Chofer" TEXT,
    "Dimension" TEXT,
    "Fecha" TEXT,
    source_id INTEGER, -- Reference to original arribos table ID
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing pendiente_desconsolidar data (Pending deconsolidation)
CREATE TABLE IF NOT EXISTS traficov2_pendiente_desconsolidar (
    id SERIAL PRIMARY KEY,
    "Contenedor" TEXT,
    "Cliente" TEXT,
    "Entrega" TEXT,
    "Vto. Vacio" TEXT,
    "Tipo" TEXT,
    "Peso" DECIMAL(10,2),
    "Cantidad" INTEGER,
    "Envase" TEXT,
    "Estado" TEXT,
    "Chofer" TEXT,
    source_id INTEGER, -- Reference to original pendiente_desconsolidar table ID
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing remisiones data (Shipments/Dispatches)
CREATE TABLE IF NOT EXISTS traficov2_remisiones (
    id SERIAL PRIMARY KEY,
    "Dia" TEXT,
    "Cliente" TEXT,
    "Booking" TEXT,
    "Contenedor" TEXT,
    "Volumen" TEXT,
    "Precinto" TEXT,
    "Observaciones" TEXT,
    "Estado" TEXT,
    "e-tally" TEXT,
    "Hora" TEXT,
    "Operacion" TEXT,
    "Chofer" TEXT,
    "Fecha y Hora Fin" TEXT,
    source_id INTEGER, -- Reference to original remisiones table ID
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for storing arribos_expo_ctns data (EXPO container arrivals - aggregated by booking)
CREATE TABLE IF NOT EXISTS traficov2_arribos_ctns_expo (
    id SERIAL PRIMARY KEY,
    "Fecha" TEXT,
    "Booking" TEXT,
    "Cliente" TEXT,
    "Cantidad" INTEGER,
    "Contenedor" TEXT,
    "Precinto" TEXT,
    "Origen" TEXT,
    "Estado" TEXT,
    "Obs." TEXT,
    "Chofer" TEXT,
    source_id INTEGER, -- Reference to original arribos_expo_ctns table ID
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_traficov2_arribos_contenedor ON traficov2_arribos("Contenedor");
CREATE INDEX IF NOT EXISTS idx_traficov2_arribos_cliente ON traficov2_arribos("Cliente");
CREATE INDEX IF NOT EXISTS idx_traficov2_arribos_source_id ON traficov2_arribos(source_id);
CREATE INDEX IF NOT EXISTS idx_traficov2_arribos_fecha_registro ON traficov2_arribos(fecha_registro);

CREATE INDEX IF NOT EXISTS idx_traficov2_pendiente_contenedor ON traficov2_pendiente_desconsolidar("Contenedor");
CREATE INDEX IF NOT EXISTS idx_traficov2_pendiente_cliente ON traficov2_pendiente_desconsolidar("Cliente");
CREATE INDEX IF NOT EXISTS idx_traficov2_pendiente_source_id ON traficov2_pendiente_desconsolidar(source_id);
CREATE INDEX IF NOT EXISTS idx_traficov2_pendiente_fecha_registro ON traficov2_pendiente_desconsolidar(fecha_registro);

CREATE INDEX IF NOT EXISTS idx_traficov2_remisiones_contenedor ON traficov2_remisiones("Contenedor");
CREATE INDEX IF NOT EXISTS idx_traficov2_remisiones_cliente ON traficov2_remisiones("Cliente");
CREATE INDEX IF NOT EXISTS idx_traficov2_remisiones_booking ON traficov2_remisiones("Booking");
CREATE INDEX IF NOT EXISTS idx_traficov2_remisiones_source_id ON traficov2_remisiones(source_id);
CREATE INDEX IF NOT EXISTS idx_traficov2_remisiones_fecha_registro ON traficov2_remisiones(fecha_registro);

CREATE INDEX IF NOT EXISTS idx_traficov2_arribos_expo_booking ON traficov2_arribos_ctns_expo("Booking");
CREATE INDEX IF NOT EXISTS idx_traficov2_arribos_expo_cliente ON traficov2_arribos_ctns_expo("Cliente");
CREATE INDEX IF NOT EXISTS idx_traficov2_arribos_expo_contenedor ON traficov2_arribos_ctns_expo("Contenedor");
CREATE INDEX IF NOT EXISTS idx_traficov2_arribos_expo_source_id ON traficov2_arribos_ctns_expo(source_id);
CREATE INDEX IF NOT EXISTS idx_traficov2_arribos_expo_fecha_registro ON traficov2_arribos_ctns_expo(fecha_registro);

-- Create a log table to track synchronization
CREATE TABLE IF NOT EXISTS traficov2_sync_log (
    id SERIAL PRIMARY KEY,
    table_name TEXT NOT NULL,
    operation TEXT NOT NULL, -- 'INSERT', 'UPDATE', 'DELETE'
    source_table TEXT NOT NULL,
    source_id INTEGER,
    target_id INTEGER,
    sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSONB
);

-- Table for storing trafico_otros data (Other traffic operations)
CREATE TABLE IF NOT EXISTS traficov2_otros (
    id SERIAL PRIMARY KEY,
    "Dia" TEXT,
    "Hora" TEXT,
    "Tipo Turno" TEXT,
    "Operacion" TEXT,
    "Cliente" TEXT,
    "Contenedor" TEXT,
    "chofer" TEXT,
    "Fecha y Hora Fin" TEXT,
    "Observaciones" TEXT,
    "Terminal" TEXT,
    "Dimension" TEXT,
    "Entrega" TEXT,
    "Cantidad" TEXT,
    "Fecha" TEXT,
    "Origen" TEXT,
    "Observaciones trafico" TEXT, 
    "Valor" TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for trafico_otros
CREATE INDEX IF NOT EXISTS idx_trafico_otros_contenedor ON trafico_otros("Contenedor");
CREATE INDEX IF NOT EXISTS idx_trafico_otros_cliente ON trafico_otros("Cliente");
CREATE INDEX IF NOT EXISTS idx_trafico_otros_operacion ON trafico_otros("Operacion");
CREATE INDEX IF NOT EXISTS idx_trafico_otros_fecha_registro ON trafico_otros(fecha_registro);

CREATE INDEX IF NOT EXISTS idx_traficov2_sync_log_table_name ON traficov2_sync_log(table_name);
CREATE INDEX IF NOT EXISTS idx_traficov2_sync_log_timestamp ON traficov2_sync_log(sync_timestamp);
CREATE INDEX IF NOT EXISTS idx_traficov2_sync_log_source_id ON traficov2_sync_log(source_id);
