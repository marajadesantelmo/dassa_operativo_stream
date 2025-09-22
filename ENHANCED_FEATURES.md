# Enhanced Traffic Management v2 Update Script

This document describes the enhanced features added to `update_traficov2.py` to include missing functionality from the original `update_trafico.py`.

## Overview

The enhanced script provides comprehensive data synchronization between operational tables and the new TráficoV2 system with advanced features for data validation, transformation, and external source integration.

## New Features

### 1. Configuration Management

The script now uses a JSON configuration file (`trafico_config.json`) for managing settings:

```json
{
    "csv_sources": {
        "enabled": true,
        "data_path": "./data/",
        "files": {
            "arribos_semana": "arribos_semana.csv",
            "pendiente_desconsolidar": "pendiente_desconsolidar.csv"
        }
    },
    "sql_server": {
        "enabled": false,
        "server": "server_address",
        "database": "database_name"
    },
    "sync_settings": {
        "arribos": {
            "batch_size": 1000,
            "validation_enabled": true,
            "retry_attempts": 3
        }
    }
}
```

### 2. Enhanced Command Line Interface

```bash
# Basic usage
python update_traficov2.py --mode incremental

# Advanced options
python update_traficov2.py --config custom_config.json --verbose
python update_traficov2.py --health-check
python update_traficov2.py --dry-run --table arribos
python update_traficov2.py --back-propagate
```

### 3. External Data Sources

#### CSV File Support
- Automatic loading of data from CSV files
- Configurable file paths and names
- Used for data backup and external validation

#### SQL Server Integration
- Optional SQL Server connectivity for validation data
- Requires `pyodbc` package
- Fetches exit/validation records for status calculation

### 4. Data Processing Features

#### Data Validation
- Container format validation (e.g., `ABCD1234567`)
- Booking format validation
- Required field checks
- Business rule enforcement

#### Data Transformation
- Container number normalization (uppercase, trimmed)
- Booking number standardization
- Date format normalization
- Field value cleanup

#### Quantity Expansion
- Expands booking records based on `Cantidad` field
- Creates multiple records for multi-container bookings
- Adds sequence numbers for tracking

#### Container Assignment
- Assigns available containers to unassigned bookings
- Sequential assignment based on booking priority
- Uses external CSV data for container availability

#### Status Calculation
- Calculates "Realizado" status from validation data
- Integrates with SQL Server exit records
- Formats status with timestamps and validation info

### 5. Performance Features

#### Batch Processing
- Configurable batch sizes per table
- Reduces memory usage for large datasets
- Progress tracking during processing

#### Retry Logic
- Automatic retry for failed operations
- Exponential backoff strategy
- Configurable retry attempts per table

#### Health Monitoring
- Database connection status
- Table row counts comparison
- Sync lag calculation
- Recent failure tracking

### 6. Advanced Synchronization

#### Conflict Resolution
- Preserves manual updates when merging
- Timestamp-based conflict resolution
- Field-level preservation (e.g., Chofer, Obs.)

#### Back-propagation
- Updates source tables with traffic data
- Synchronizes chofer assignments
- Maintains data consistency across systems

#### Delta Detection
- Timestamp-based change detection
- Incremental sync optimization
- Last sync time tracking

## Usage Examples

### Basic Synchronization
```bash
# Incremental sync (default)
python update_traficov2.py

# Full sync
python update_traficov2.py --mode full

# Single table sync
python update_traficov2.py --table arribos --verbose
```

### Health Monitoring
```bash
# Check system health
python update_traficov2.py --health-check

# Output:
# === System Health Check ===
# Database Connection: ✓
# Failed Syncs (24h): 0
# Table Row Counts:
#   arribos: 1250 ✓
#   traficov2_arribos: 1245 ✓
# Sync Lag (hours):
#   traficov2_arribos: 0.5h
```

### Testing and Validation
```bash
# Dry run to see what would be done
python update_traficov2.py --dry-run

# Back-propagate chofer assignments
python update_traficov2.py --back-propagate

# Custom configuration
python update_traficov2.py --config production_config.json
```

## Configuration Options

### CSV Sources
```json
"csv_sources": {
    "enabled": true,
    "data_path": "./data/",
    "files": {
        "arribos_semana": "arribos_semana.csv",
        "pendiente_desconsolidar": "pendiente_desconsolidar.csv",
        "remisiones_semana": "remisiones_semana.csv",
        "arribos_expo_ctns": "arribos_expo_semana_ctns.csv"
    }
}
```

### SQL Server Integration
```json
"sql_server": {
    "enabled": true,
    "server": "101.44.8.58\\SQLEXPRESS_X86,1436",
    "database": "DEPOFIS",
    "schema": "DASSA",
    "table": "Salidas",
    "username": "your_username",
    "password": "your_password"
}
```

### Sync Settings
```json
"sync_settings": {
    "arribos": {
        "batch_size": 1000,
        "validation_enabled": true,
        "retry_attempts": 3
    },
    "arribos_expo_ctns": {
        "batch_size": 500,
        "container_assignment": true,
        "quantity_expansion": true,
        "retry_attempts": 3
    }
}
```

### Business Rules
```json
"business_rules": {
    "container_validation": {
        "required_fields": ["Contenedor", "Booking"],
        "container_format_regex": "^[A-Z]{4}[0-9]{7}$"
    },
    "booking_validation": {
        "required_fields": ["Booking", "Cliente"],
        "booking_format_regex": "^[A-Z0-9]{8,12}$"
    }
}
```

## Testing

Run the comprehensive test suite:

```bash
python test_enhanced_features.py
```

Tests cover:
- Configuration loading
- Data validation
- Data transformation
- Quantity expansion
- Health checks
- CSV data loading

## Dependencies

### Required
- pandas
- supabase (supabase-py)
- Standard library modules

### Optional
- pyodbc (for SQL Server support)
- psutil (for system monitoring)
- schedule (for scheduled runs)

## Migration from Original Script

The enhanced script maintains full backward compatibility. To migrate:

1. Replace calls to `update_trafico.py` with `update_traficov2.py`
2. Create a configuration file if you need custom settings
3. Test with `--dry-run` first
4. Use `--health-check` to verify system status

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Check credentials and network connectivity
2. **CSV File Not Found**: Verify paths in configuration file
3. **SQL Server Issues**: Ensure pyodbc is installed and configured
4. **Validation Errors**: Check business rules configuration

### Debug Mode
```bash
python update_traficov2.py --verbose --dry-run
```

### Health Check
```bash
python update_traficov2.py --health-check
```

## Performance Tuning

- Adjust `batch_size` for memory optimization
- Set appropriate `retry_attempts` for reliability
- Enable CSV caching for backup and validation
- Use incremental mode for regular syncs
- Schedule health checks for monitoring