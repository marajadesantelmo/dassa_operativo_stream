# Traffic Management Module v2

This document describes the new Traffic Management Module v2 implementation for the DASSA operational dashboard system.

## Overview

The Traffic Management v2 module provides enhanced traffic management capabilities by synchronizing data from existing operational tables to new dedicated traficov2 tables. This allows for better performance, specialized traffic management features, and improved data organization.

## Architecture

### Source Tables
The system synchronizes data from these existing operational tables:
- `arribos` - IMPO arrivals from ports to DASSA
- `pendiente_desconsolidar` - Pending deconsolidation containers
- `remisiones` - Shipments/dispatches from DASSA to ports
- `arribos_expo_ctns` - EXPO container arrivals (aggregated by booking)

### Target Tables
Data is synchronized to these new traficov2 tables:
- `traficov2_arribos` - IMPO arrivals with traffic management metadata
- `traficov2_pendiente_desconsolidar` - Pending deconsolidation with tracking
- `traficov2_remisiones` - Shipments with enhanced management features
- `traficov2_arribos_ctns_expo` - EXPO container arrivals aggregated by booking

### Special Features

#### Booking Aggregation
The `arribos_expo_ctns` data is processed specially:
- Multiple containers for the same booking are aggregated into a single record
- Container names are concatenated (e.g., "CONT-001, CONT-002")
- Quantities are summed
- Other fields use the first occurrence values

#### Change Detection
The synchronization script implements intelligent change detection:
- Only modified records are updated
- New records are inserted
- Tracking metadata (source_id, modification timestamps) is maintained

## Files

### SQL Schema
- `create_tables_traficov2.sql` - Contains all SQL statements to create the traficov2 tables in Supabase

### Synchronization Script
- `update_traficov2.py` - Main synchronization script
- `test_traficov2_sync.py` - Unit tests for synchronization logic
- `mock_update_traficov2.py` - Mock version for testing without database connection

## Usage

### Creating Tables
Execute the SQL file in your Supabase instance:
```sql
-- Run the entire create_tables_traficov2.sql file
```

### Running Synchronization

#### Full Synchronization
Synchronizes all data from source tables to target tables:
```bash
python update_traficov2.py --mode full
```

#### Incremental Synchronization
Synchronizes only changes since last sync (default mode):
```bash
python update_traficov2.py --mode incremental
```

#### Single Table Synchronization
Synchronize a specific table only:
```bash
python update_traficov2.py --table arribos --mode full
```

#### Verbose Output
Enable detailed logging:
```bash
python update_traficov2.py --mode full --verbose
```

### Testing
Run the test suite to verify synchronization logic:
```bash
python test_traficov2_sync.py
```

Run mock synchronization for testing:
```bash
python mock_update_traficov2.py --mode full
```

## Configuration

### Environment Variables
Ensure these environment variables are set:
- `url_supabase` - Your Supabase project URL
- `key_supabase` - Your Supabase API key

### Sync Mappings
The script uses predefined mappings in `update_traficov2.py`:

```python
sync_mappings = {
    'arribos': {
        'target': 'traficov2_arribos',
        'key_columns': ['Contenedor'],  # Business key for uniqueness
        'exclude_columns': ['id']       # Columns to exclude from sync
    },
    # ... other mappings
}
```

## Monitoring

### Sync Logs
The synchronization process is logged to:
- `traficov2_sync.log` - File-based logging
- Console output - Real-time monitoring

### Database Tracking
The `traficov2_sync_log` table tracks all synchronization operations:
- Operation type (INSERT, UPDATE, DELETE)
- Source and target record IDs
- Timestamps
- Operation details

## Scheduling

For production use, consider scheduling the synchronization script:

### Cron Example
```bash
# Run every 15 minutes
*/15 * * * * cd /path/to/dassa_operativo_stream && python update_traficov2.py --mode incremental

# Full sync daily at 2 AM
0 2 * * * cd /path/to/dassa_operativo_stream && python update_traficov2.py --mode full
```

### Python Scheduler Example
```python
import schedule
import time

def sync_traffic_data():
    # Run incremental sync
    os.system("python update_traficov2.py --mode incremental")

# Schedule incremental sync every 15 minutes
schedule.every(15).minutes.do(sync_traffic_data)

while True:
    schedule.run_pending()
    time.sleep(60)
```

## Troubleshooting

### Common Issues

#### Connection Errors
```
SupabaseException: supabase_url is required
```
**Solution**: Ensure environment variables `url_supabase` and `key_supabase` are set.

#### Missing Tables
```
Error syncing table arribos: relation "traficov2_arribos" does not exist
```
**Solution**: Run the `create_tables_traficov2.sql` script in Supabase first.

#### Data Type Errors
Check that source data types match the target table schema. The script handles basic type conversion but complex data may need preprocessing.

### Performance Tips

1. **Use Incremental Mode**: For regular operations, use incremental sync to minimize processing time
2. **Monitor Log Size**: The sync log table can grow large; consider periodic cleanup
3. **Index Optimization**: The provided indexes should handle most queries efficiently

## Data Examples

### Arribos Data Structure
```python
{
    "Terminal": "Trp - Terminales 1-2-3",
    "Turno": "03:00", 
    "Contenedor": "OOCU-048760-4",
    "Cliente": "Lift Van Int. Co S.A",
    "Booking": "COSU6426848340",
    "Estado": "Pendiente arribo",
    "Chofer": None,
    "Dimension": "30"
}
```

### Aggregated EXPO Container Data
```python
# Before aggregation (2 records)
[
    {"Booking": "64179524", "Cantidad": 1, "Contenedor": "TCLU-953831-4"},
    {"Booking": "64179524", "Cantidad": 1, "Contenedor": "FANU-117537-6"}
]

# After aggregation (1 record)
{
    "Booking": "64179524", 
    "Cantidad": 2, 
    "Contenedor": "TCLU-953831-4, FANU-117537-6"
}
```