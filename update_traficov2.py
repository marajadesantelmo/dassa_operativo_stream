#!/usr/bin/env python3
"""
Traffic Management v2 Update Script

This script synchronizes data from the existing operational tables to the new 
traficov2 tables for the Traffic Management Module v2.

Source tables:
- arribos (IMPO arrivals)
- pendiente_desconsolidar (Pending deconsolidation)
- remisiones (Shipments/Dispatches) 
- arribos_expo_ctns (EXPO container arrivals - aggregated by booking)

Target tables:
- traficov2_arribos
- traficov2_pendiente_desconsolidar
- traficov2_remisiones
- traficov2_arribos_ctns_expo

The script handles incremental updates and change detection.
"""

import pandas as pd
import os
import sys
import re
import time
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from supabase_connection2 import (
    fetch_table_data, 
    insert_data, 
    update_data, 
    supabase_client
)

# Optional SQL Server support
try:
    import pyodbc
    SQL_SERVER_AVAILABLE = True
except ImportError:
    SQL_SERVER_AVAILABLE = False
    logging.warning("pyodbc not available - SQL Server features disabled")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traficov2_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TraficoV2Synchronizer:
    """Handles synchronization between source and target tables for Traffic Management v2"""
    
    def __init__(self, config_file: str = 'trafico_config.json'):
        self.config = self.load_config(config_file)
        self.sync_mappings = {
            'arribos': {
                'target': 'traficov2_arribos',
                'key_columns': ['Contenedor'],  # Primary business key
                'exclude_columns': ['id']  # Columns to exclude from sync
            },
            'pendiente_desconsolidar': {
                'target': 'traficov2_pendiente_desconsolidar', 
                'key_columns': ['Contenedor'],
                'exclude_columns': ['id']
            },
            'remisiones': {
                'target': 'traficov2_remisiones',
                'key_columns': ['Contenedor', 'Operacion'],  # Combination for uniqueness
                'exclude_columns': ['id']
            },
            'arribos_expo_ctns': {
                'target': 'traficov2_arribos_ctns_expo',
                'key_columns': ['Booking'],  # Aggregated by booking
                'exclude_columns': ['id'],
                'aggregate_by_booking': True  # Special handling for this table
            }
        }
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                logger.info(f"Configuration loaded from {config_file}")
                return config
            else:
                logger.warning(f"Configuration file {config_file} not found, using defaults")
                return self.get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "csv_sources": {"enabled": False},
            "sql_server": {"enabled": False},
            "sync_settings": {},
            "business_rules": {},
            "archival": {"enabled": False}
        }
    
    def load_external_data_sources(self) -> Dict[str, pd.DataFrame]:
        """Load data from CSV files and SQL Server"""
        sources = {}
        
        # Load CSV sources
        if self.config.get('csv_sources', {}).get('enabled', False):
            csv_config = self.config['csv_sources']
            data_path = csv_config.get('data_path', './data/')
            csv_files = csv_config.get('files', {})
            
            for key, filename in csv_files.items():
                file_path = os.path.join(data_path, filename)
                try:
                    if os.path.exists(file_path):
                        sources[key] = pd.read_csv(file_path)
                        logger.info(f"Loaded CSV data from {filename}: {len(sources[key])} records")
                    else:
                        logger.warning(f"CSV file not found: {file_path}")
                except Exception as e:
                    logger.error(f"Error loading CSV file {filename}: {e}")
        
        # Load SQL Server validation data
        if self.config.get('sql_server', {}).get('enabled', False) and SQL_SERVER_AVAILABLE:
            try:
                sources['salidas'] = self.fetch_sql_validation_data()
            except Exception as e:
                logger.error(f"Error loading SQL Server data: {e}")
        
        return sources
    
    def fetch_sql_validation_data(self) -> pd.DataFrame:
        """Fetch validation data from SQL Server"""
        if not SQL_SERVER_AVAILABLE:
            logger.error("SQL Server support not available")
            return pd.DataFrame()
        
        sql_config = self.config['sql_server']
        server = sql_config['server']
        database = sql_config['database']
        schema = sql_config['schema']
        table = sql_config['table']
        username = sql_config.get('username', '')
        password = sql_config.get('password', '')
        
        try:
            # Calculate date range for recent data
            fecha_ant = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
            conn = pyodbc.connect(conn_str)
            
            query = f"""
                SELECT contenedor, fecha_egr, validada   
                FROM [{database}].[{schema}].[{table}] 
                WHERE fecha_egr > '{fecha_ant}'
            """
            
            df = pd.read_sql(query, conn)
            conn.close()
            
            logger.info(f"Loaded SQL validation data: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching SQL validation data: {e}")
            return pd.DataFrame()
    
    def validate_record(self, record: Dict, table_name: str) -> Tuple[bool, List[str]]:
        """Validate record against business rules"""
        errors = []
        business_rules = self.config.get('business_rules', {})
        
        if table_name == 'arribos' or table_name == 'arribos_expo_ctns':
            # Container validation
            container_rules = business_rules.get('container_validation', {})
            required_fields = container_rules.get('required_fields', [])
            
            for field in required_fields:
                if not record.get(field):
                    errors.append(f"{field} is required")
            
            # Container format validation
            if record.get('Contenedor'):
                container_regex = container_rules.get('container_format_regex', '')
                if container_regex and not re.match(container_regex, str(record['Contenedor'])):
                    errors.append(f"Invalid container format: {record['Contenedor']}")
        
        if table_name == 'arribos_expo_ctns':
            # Booking validation
            booking_rules = business_rules.get('booking_validation', {})
            required_fields = booking_rules.get('required_fields', [])
            
            for field in required_fields:
                if not record.get(field):
                    errors.append(f"{field} is required")
            
            # Booking format validation
            if record.get('Booking'):
                booking_regex = booking_rules.get('booking_format_regex', '')
                if booking_regex and not re.match(booking_regex, str(record['Booking'])):
                    errors.append(f"Invalid booking format: {record['Booking']}")
            
            # Quantity validation
            if record.get('Cantidad', 0) <= 0:
                errors.append("Quantity must be greater than 0")
        
        return len(errors) == 0, errors
    
    def transform_record(self, record: Dict, source_table: str) -> Dict:
        """Apply transformations to records before sync"""
        transformed = record.copy()
        
        if source_table in ['arribos', 'arribos_expo_ctns']:
            # Normalize container numbers
            if 'Contenedor' in transformed and transformed['Contenedor']:
                transformed['Contenedor'] = str(transformed['Contenedor']).upper().strip()
        
        if source_table == 'arribos_expo_ctns':
            # Normalize booking numbers
            if 'Booking' in transformed and transformed['Booking']:
                transformed['Booking'] = str(transformed['Booking']).upper().strip()
        
        # Standardize dates
        date_fields = ['Fecha', 'Vto. Vacio', 'fecha_egr']
        for field in date_fields:
            if field in transformed and transformed[field]:
                try:
                    # Normalize date format
                    if isinstance(transformed[field], str):
                        parsed_date = pd.to_datetime(transformed[field], errors='coerce')
                        if not pd.isna(parsed_date):
                            transformed[field] = parsed_date.strftime('%d/%m/%Y')
                except Exception as e:
                    logger.warning(f"Error normalizing date field {field}: {e}")
        
        return transformed
    
    def expand_records_by_quantity(self, df: pd.DataFrame, source_table: str) -> pd.DataFrame:
        """Expand records based on quantity field for export containers"""
        if source_table != 'arribos_expo_ctns' or df.empty:
            return df
        
        if 'Cantidad' not in df.columns:
            return df
        
        try:
            # Expand records based on quantity
            expanded_records = []
            
            for _, row in df.iterrows():
                cantidad = int(row.get('Cantidad', 1))
                if cantidad <= 0:
                    cantidad = 1
                
                # Create multiple records for each quantity
                for i in range(cantidad):
                    expanded_record = row.copy()
                    # Add sequence number if needed
                    if cantidad > 1:
                        expanded_record['Secuencia'] = i + 1
                    expanded_records.append(expanded_record)
            
            if expanded_records:
                expanded_df = pd.DataFrame(expanded_records).reset_index(drop=True)
                logger.info(f"Expanded {len(df)} records to {len(expanded_df)} records based on quantity")
                return expanded_df
            
        except Exception as e:
            logger.error(f"Error expanding records by quantity: {e}")
        
        return df
    
    def resolve_conflicts(self, source_record: Dict, target_record: Dict) -> Dict:
        """Resolve conflicts between source and target records"""
        resolved = source_record.copy()
        
        # Keep target modifications if they're newer
        if (target_record.get('fecha_modificacion') and 
            source_record.get('fecha_modificacion')):
            try:
                target_time = datetime.fromisoformat(target_record['fecha_modificacion'].replace('Z', ''))
                source_time = datetime.fromisoformat(source_record['fecha_modificacion'].replace('Z', ''))
                
                if target_time > source_time:
                    # Keep certain target fields that might have been manually updated
                    preserve_fields = ['Chofer', 'Obs.', 'Estado']
                    for field in preserve_fields:
                        if field in target_record and target_record[field]:
                            resolved[field] = target_record[field]
                            logger.debug(f"Preserved field {field} from target record")
            except Exception as e:
                logger.warning(f"Error resolving conflict: {e}")
        
        return resolved
    
    def retry_operation(self, operation_func, max_retries: int = 3, delay: float = 1.0):
        """Retry failed operations with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return operation_func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                wait_time = delay * (2 ** attempt)
                logger.warning(f"Operation failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
    
    def assign_containers_to_bookings(self, source_df: pd.DataFrame, external_sources: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Handle complex container assignment logic for export bookings"""
        if source_df.empty or 'arribos_expo_ctns' not in external_sources:
            return source_df
        
        try:
            # Get the CSV data with container information
            arribos_with_containers = external_sources['arribos_expo_ctns']
            
            if arribos_with_containers.empty:
                return source_df
            
            # Find records without containers assigned
            no_container_mask = (source_df['Contenedor'].isna() | 
                               (source_df['Contenedor'] == '-') | 
                               (source_df['Contenedor'] == ''))
            
            records_without_containers = source_df[no_container_mask].copy()
            
            if records_without_containers.empty:
                return source_df
            
            # For each booking, try to assign available containers
            for booking in records_without_containers['Booking'].unique():
                booking_records = records_without_containers[records_without_containers['Booking'] == booking]
                
                # Find available containers for this booking
                available_containers = arribos_with_containers[
                    (arribos_with_containers['Booking'] == booking) & 
                    (arribos_with_containers['Contenedor'].notna()) &
                    (arribos_with_containers['Contenedor'] != '-')
                ]
                
                if not available_containers.empty:
                    # Assign containers sequentially
                    container_list = available_containers['Contenedor'].tolist()
                    
                    for idx, (record_idx, record) in enumerate(booking_records.iterrows()):
                        if idx < len(container_list):
                            source_df.loc[record_idx, 'Contenedor'] = container_list[idx]
                            logger.debug(f"Assigned container {container_list[idx]} to booking {booking}")
            
            return source_df
            
        except Exception as e:
            logger.error(f"Error in container assignment: {e}")
            return source_df
    
    def calculate_realizado_status(self, df: pd.DataFrame, external_sources: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Calculate 'Realizado' status based on external validation data"""
        if df.empty or 'salidas' not in external_sources:
            return df
        
        try:
            salidas_df = external_sources['salidas']
            if salidas_df.empty:
                return df
            
            # Mark records as "Realizado" if they exist in validation data
            for idx, row in df.iterrows():
                container = row.get('Contenedor')
                if container and container in salidas_df['contenedor'].values:
                    # Find the exit record
                    exit_record = salidas_df[salidas_df['contenedor'] == container].iloc[0]
                    fecha_egr = exit_record.get('fecha_egr', '')
                    validada = exit_record.get('validada', '')
                    
                    # Format the "Realizado" status
                    if fecha_egr:
                        fecha_egr_formatted = pd.to_datetime(fecha_egr).strftime('%d/%m/%Y %H:%M')
                        realizado_value = f"Realizado {fecha_egr_formatted} {validada}"
                        df.loc[idx, 'Estado'] = realizado_value
                        logger.debug(f"Marked container {container} as {realizado_value}")
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating realizado status: {e}")
            return df
    
    def update_source_tables(self, updates_map: Dict[str, Dict]) -> None:
        """Update source tables with data from traffic tables (back-propagation)"""
        for source_table, field_updates in updates_map.items():
            try:
                # Get target table data
                target_table = self.sync_mappings[source_table]['target']
                target_df = fetch_table_data(target_table)
                
                if target_df.empty:
                    continue
                
                # Update chofer information in source table
                if 'chofer' in field_updates:
                    chofer_updates = {}
                    
                    # Create chofer mapping from target data
                    for _, row in target_df.iterrows():
                        if pd.notna(row.get('Chofer')) and row.get('Chofer') not in [None, 'None', '']:
                            container = row.get('Contenedor')
                            if container:
                                chofer_updates[container] = row['Chofer']
                    
                    # Apply updates to source table
                    source_df = fetch_table_data(source_table)
                    for idx, row in source_df.iterrows():
                        container = row.get('Contenedor')
                        if container in chofer_updates:
                            new_chofer = chofer_updates[container]
                            if row.get('Chofer') != new_chofer:
                                # Update the source record
                                try:
                                    update_data(source_table, row['id'], {'Chofer': new_chofer})
                                    logger.info(f"Updated chofer for {container} in {source_table}")
                                except Exception as e:
                                    logger.error(f"Error updating chofer for {container}: {e}")
                
            except Exception as e:
                logger.error(f"Error updating source table {source_table}: {e}")
    
    def save_data_to_csv(self, df: pd.DataFrame, table_name: str) -> None:
        """Save synchronized data to local CSV files"""
        try:
            csv_config = self.config.get('csv_sources', {})
            if not csv_config.get('enabled', False):
                return
            
            data_path = csv_config.get('data_path', './data/')
            os.makedirs(data_path, exist_ok=True)
            
            filename = f"{table_name}.csv"
            file_path = os.path.join(data_path, filename)
            
            df.to_csv(file_path, index=False)
            logger.info(f"Saved {len(df)} records to {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving CSV for {table_name}: {e}")
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform health checks on sync system"""
        health_status = {
            'database_connection': self.check_database_connection(),
            'table_counts': self.get_table_row_counts(),
            'last_sync_times': self.get_all_last_sync_times(),
            'sync_lag': self.calculate_sync_lag(),
            'failed_syncs_24h': self.count_recent_failures()
        }
        
        return health_status
    
    def check_database_connection(self) -> bool:
        """Check if database connection is working"""
        try:
            # Simple query to test connection
            result = supabase_client.from_('traficov2_sync_log').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    def get_table_row_counts(self) -> Dict[str, int]:
        """Get row counts for all sync tables"""
        counts = {}
        
        for source_table, config in self.sync_mappings.items():
            target_table = config['target']
            
            try:
                source_df = fetch_table_data(source_table)
                counts[source_table] = len(source_df)
                
                target_df = fetch_table_data(target_table)
                counts[target_table] = len(target_df)
                
            except Exception as e:
                logger.error(f"Error getting row count for {source_table}/{target_table}: {e}")
                counts[source_table] = -1
                counts[target_table] = -1
        
        return counts
    
    def get_all_last_sync_times(self) -> Dict[str, Optional[str]]:
        """Get last sync times for all tables"""
        sync_times = {}
        
        for source_table, config in self.sync_mappings.items():
            target_table = config['target']
            last_sync = self.get_last_sync_time(target_table)
            sync_times[target_table] = last_sync.isoformat() if last_sync else None
        
        return sync_times
    
    def calculate_sync_lag(self) -> Dict[str, float]:
        """Calculate sync lag in hours for each table"""
        lag_hours = {}
        current_time = datetime.now()
        
        for source_table, config in self.sync_mappings.items():
            target_table = config['target']
            last_sync = self.get_last_sync_time(target_table)
            
            if last_sync:
                lag = (current_time - last_sync).total_seconds() / 3600
                lag_hours[target_table] = round(lag, 2)
            else:
                lag_hours[target_table] = float('inf')
        
        return lag_hours
    
    def count_recent_failures(self) -> int:
        """Count failed syncs in the last 24 hours"""
        try:
            yesterday = datetime.now() - timedelta(days=1)
            
            result = (supabase_client
                     .from_('traficov2_sync_log')
                     .select('id')
                     .eq('operation', 'ERROR')
                     .gte('sync_timestamp', yesterday.isoformat())
                     .execute())
            
            return len(result.data) if result.data else 0
            
        except Exception as e:
            logger.error(f"Error counting recent failures: {e}")
            return -1
        
    def log_sync_operation(self, table_name: str, operation: str, source_table: str, 
                          source_id: int = None, target_id: int = None, details: Dict = None):
        """Log synchronization operations to traficov2_sync_log table"""
        try:
            log_entry = {
                'table_name': table_name,
                'operation': operation,
                'source_table': source_table,
                'source_id': source_id,
                'target_id': target_id,
                'details': details
            }
            supabase_client.from_('traficov2_sync_log').insert(log_entry).execute()
            logger.info(f"Logged {operation} operation for {table_name}")
        except Exception as e:
            logger.error(f"Failed to log sync operation: {e}")
    
    def get_last_sync_time(self, table_name: str) -> Optional[datetime]:
        """Get the last successful sync time for a table"""
        try:
            result = (supabase_client
                     .from_('traficov2_sync_log')
                     .select('sync_timestamp')
                     .eq('table_name', table_name)
                     .order('sync_timestamp', desc=True)
                     .limit(1)
                     .execute())
            
            if result.data:
                return datetime.fromisoformat(result.data[0]['sync_timestamp'].replace('Z', '+00:00'))
            return None
        except Exception as e:
            logger.warning(f"Could not get last sync time for {table_name}: {e}")
            return None
    
    def compare_records(self, source_record: Dict, target_record: Dict, exclude_columns: List[str]) -> bool:
        """Compare source and target records to detect changes"""
        for key, value in source_record.items():
            if key in exclude_columns or key in ['fecha_registro', 'fecha_modificacion']:
                continue
            if str(value) != str(target_record.get(key, '')):
                return True
        return False
    
    def prepare_record_for_sync(self, record: Dict, exclude_columns: List[str], source_id: int = None) -> Dict:
        """Prepare a record for insertion/update in target table"""
        cleaned_record = {}
        for key, value in record.items():
            if key not in exclude_columns:
                cleaned_record[key] = value
        
        # Handle cases where source_id might be None (when no 'id' column exists)
        if source_id is not None:
            cleaned_record['source_id'] = source_id
        elif 'source_id' in record:
            # Use the source_id that was created during aggregation
            cleaned_record['source_id'] = record['source_id']
        
        cleaned_record['fecha_modificacion'] = datetime.now().isoformat()
        
        return cleaned_record
    
    def aggregate_arribos_expo_by_booking(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate arribos_expo_ctns data by booking"""
        if df.empty:
            return df
            
        # Check if required columns exist
        required_columns = ['Booking']
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns in arribos_expo_ctns. Available columns: {df.columns.tolist()}")
            return pd.DataFrame()
        
        # Define aggregation rules based on available columns
        agg_rules = {}
        
        # Standard columns that should be aggregated
        column_mappings = {
            'Fecha': 'first',
            'Cliente': 'first',
            'Cantidad': 'sum',
            'Contenedor': lambda x: ', '.join(x.dropna().astype(str).unique()) if len(x.dropna()) > 0 else '-',
            'Precinto': 'first',
            'Origen': 'first',
            'Estado': 'first',
            'Obs.': 'first',
            'Chofer': 'first'
        }
        
        # Only include columns that exist in the dataframe
        for col, agg_func in column_mappings.items():
            if col in df.columns:
                agg_rules[col] = agg_func
        
        # Handle the ID column - use row index if 'id' column doesn't exist
        if 'id' in df.columns:
            agg_rules['id'] = 'first'
        else:
            # Create a temporary ID based on row index for source reference
            df = df.reset_index()
            agg_rules['index'] = 'first'
            logger.warning("No 'id' column found in arribos_expo_ctns, using row index as source reference")
        
        try:
            # Group by booking and aggregate
            aggregated = df.groupby('Booking').agg(agg_rules).reset_index()
            
            # If we used index instead of id, rename it to source_id for database compatibility
            if 'index' in aggregated.columns and 'id' not in aggregated.columns:
                aggregated = aggregated.rename(columns={'index': 'source_id'})
            
            return aggregated
            
        except Exception as e:
            logger.error(f"Error during aggregation: {e}")
            logger.error(f"DataFrame columns: {df.columns.tolist()}")
            logger.error(f"Aggregation rules: {agg_rules}")
            return pd.DataFrame()
    
    def sync_table(self, source_table: str, full_sync: bool = False) -> Dict[str, int]:
        """Sync a source table to its corresponding target table"""
        logger.info(f"Starting sync for table: {source_table}")
        
        config = self.sync_mappings.get(source_table)
        if not config:
            logger.error(f"No sync configuration found for table: {source_table}")
            return {'inserted': 0, 'updated': 0, 'errors': 0}
        
        target_table = config['target']
        key_columns = config['key_columns']
        exclude_columns = config['exclude_columns']
        
        # Get sync settings for this table
        sync_settings = self.config.get('sync_settings', {}).get(source_table, {})
        batch_size = sync_settings.get('batch_size', 1000)
        retry_attempts = sync_settings.get('retry_attempts', 3)
        
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        try:
            # Load external data sources if needed
            external_sources = self.load_external_data_sources()
            
            # Fetch source data with retry mechanism
            logger.info(f"Fetching data from source table: {source_table}")
            source_df = self.retry_operation(
                lambda: fetch_table_data(source_table),
                max_retries=retry_attempts
            )
            
            if source_df.empty:
                logger.warning(f"Source table {source_table} is empty")
                return stats
            
            # Apply data transformations
            logger.info("Applying data transformations")
            for idx, row in source_df.iterrows():
                transformed_record = self.transform_record(row.to_dict(), source_table)
                for col, value in transformed_record.items():
                    source_df.loc[idx, col] = value
            
            # Expand records by quantity if configured
            if sync_settings.get('quantity_expansion', False):
                source_df = self.expand_records_by_quantity(source_df, source_table)
            
            # Assign containers to bookings if configured
            if sync_settings.get('container_assignment', False):
                source_df = self.assign_containers_to_bookings(source_df, external_sources)
            
            # Calculate realizado status if validation data available
            if sync_settings.get('status_validation', False):
                source_df = self.calculate_realizado_status(source_df, external_sources)
            
            # Special handling for arribos_expo_ctns - aggregate by booking
            if config.get('aggregate_by_booking'):
                logger.info("Aggregating arribos_expo_ctns data by booking")
                source_df = self.aggregate_arribos_expo_by_booking(source_df)
                
                # If aggregation failed, return with error
                if source_df.empty:
                    logger.error("Aggregation failed, no data to sync")
                    stats['errors'] += 1
                    return stats
            
            # Fetch existing target data with retry mechanism
            logger.info(f"Fetching existing data from target table: {target_table}")
            try:
                target_df = self.retry_operation(
                    lambda: fetch_table_data(target_table),
                    max_retries=retry_attempts
                )
            except Exception as e:
                logger.warning(f"Target table {target_table} might not exist or be empty: {e}")
                target_df = pd.DataFrame()
            
            # Process records in batches
            total_records = len(source_df)
            total_batches = (total_records + batch_size - 1) // batch_size
            
            logger.info(f"Processing {total_records} records in {total_batches} batches")
            
            # Create lookup dictionary for existing records
            existing_records = {}
            if not target_df.empty:
                for _, row in target_df.iterrows():
                    # Create composite key from key columns
                    key_values = []
                    for col in key_columns:
                        key_values.append(str(row.get(col, '')))
                    composite_key = '|'.join(key_values)
                    existing_records[composite_key] = row.to_dict()
            
            # Process each batch
            for batch_num in range(total_batches):
                start_idx = batch_num * batch_size
                end_idx = min(start_idx + batch_size, total_records)
                batch_df = source_df.iloc[start_idx:end_idx]
                
                logger.info(f"Processing batch {batch_num + 1}/{total_batches} ({len(batch_df)} records)")
                
                batch_stats = self.process_batch(batch_df, target_table, key_columns, exclude_columns, existing_records, sync_settings)
                
                # Aggregate batch stats
                for key in stats:
                    stats[key] += batch_stats[key]
            
            # Save data to CSV if configured
            self.save_data_to_csv(source_df, source_table)
            
            logger.info(f"Sync completed for {source_table}. Stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error syncing table {source_table}: {e}")
            stats['errors'] += 1
            return stats
    
    def process_batch(self, batch_df: pd.DataFrame, target_table: str, key_columns: List[str], 
                     exclude_columns: List[str], existing_records: Dict[str, Dict], 
                     sync_settings: Dict[str, Any]) -> Dict[str, int]:
        """Process a batch of records"""
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        for _, source_row in batch_df.iterrows():
            try:
                # Create composite key
                key_values = []
                for col in key_columns:
                    key_values.append(str(source_row.get(col, '')))
                composite_key = '|'.join(key_values)
                
                source_record = source_row.to_dict()
                
                # Validate record if validation is enabled
                if sync_settings.get('validation_enabled', False):
                    is_valid, errors = self.validate_record(source_record, target_table)
                    if not is_valid:
                        logger.warning(f"Record validation failed for {composite_key}: {errors}")
                        stats['errors'] += 1
                        continue
                
                source_id = source_record.get('id')
                
                # Handle case where there's no 'id' column but we have source_id from aggregation
                if source_id is None and 'source_id' in source_record:
                    source_id = source_record['source_id']
                
                if composite_key in existing_records:
                    # Record exists - check if update needed
                    existing_record = existing_records[composite_key]
                    
                    # Resolve conflicts between source and target
                    resolved_record = self.resolve_conflicts(source_record, existing_record)
                    
                    if self.compare_records(resolved_record, existing_record, exclude_columns):
                        # Update needed
                        target_record = self.prepare_record_for_sync(resolved_record, exclude_columns, source_id)
                        
                        self.retry_operation(
                            lambda: update_data(target_table, existing_record['id'], target_record),
                            max_retries=sync_settings.get('retry_attempts', 3)
                        )
                        
                        self.log_sync_operation(
                            target_table, 'UPDATE', target_table.replace('traficov2_', ''), 
                            source_id, existing_record['id'],
                            {'changes_detected': True}
                        )
                        stats['updated'] += 1
                        logger.debug(f"Updated record with key: {composite_key}")
                else:
                    # New record - insert
                    target_record = self.prepare_record_for_sync(source_record, exclude_columns, source_id)
                    
                    result = self.retry_operation(
                        lambda: insert_data(target_table, target_record),
                        max_retries=sync_settings.get('retry_attempts', 3)
                    )
                    
                    # Get the inserted record ID from result
                    inserted_id = None
                    if result.data:
                        inserted_id = result.data[0].get('id')
                    
                    self.log_sync_operation(
                        target_table, 'INSERT', target_table.replace('traficov2_', ''),
                        source_id, inserted_id,
                        {'new_record': True}
                    )
                    stats['inserted'] += 1
                    logger.debug(f"Inserted new record with key: {composite_key}")
                    
            except Exception as e:
                logger.error(f"Error processing record {composite_key}: {e}")
                stats['errors'] += 1
                continue
        
        return stats
    
    def run_full_sync(self) -> Dict[str, Dict[str, int]]:
        """Run a full synchronization of all tables"""
        logger.info("Starting full synchronization of all traffic v2 tables")
        
        overall_stats = {}
        
        for source_table in self.sync_mappings.keys():
            stats = self.sync_table(source_table, full_sync=True)
            overall_stats[source_table] = stats
        
        logger.info("Full synchronization completed")
        logger.info(f"Overall stats: {overall_stats}")
        
        return overall_stats
    
    def run_incremental_sync(self) -> Dict[str, Dict[str, int]]:
        """Run an incremental synchronization based on last sync times"""
        logger.info("Starting incremental synchronization")
        
        overall_stats = {}
        
        for source_table in self.sync_mappings.keys():
            last_sync = self.get_last_sync_time(self.sync_mappings[source_table]['target'])
            if last_sync:
                logger.info(f"Last sync for {source_table}: {last_sync}")
            else:
                logger.info(f"No previous sync found for {source_table}, running full sync")
                
            stats = self.sync_table(source_table, full_sync=not bool(last_sync))
            overall_stats[source_table] = stats
        
        logger.info("Incremental synchronization completed")
        logger.info(f"Overall stats: {overall_stats}")
        
        return overall_stats


def main():
    """Main function to run the synchronization"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Traffic Management v2 Synchronization Script')
    parser.add_argument('--mode', choices=['full', 'incremental'], default='incremental',
                       help='Synchronization mode (default: incremental)')
    parser.add_argument('--table', help='Sync specific table only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--config', default='trafico_config.json', 
                       help='Configuration file path (default: trafico_config.json)')
    parser.add_argument('--health-check', action='store_true',
                       help='Perform health check and exit')
    parser.add_argument('--back-propagate', action='store_true',
                       help='Update source tables with traffic data')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    synchronizer = TraficoV2Synchronizer(config_file=args.config)
    
    try:
        if args.health_check:
            # Perform health check
            health_status = synchronizer.perform_health_check()
            print("\n=== System Health Check ===")
            print(f"Database Connection: {'✓' if health_status['database_connection'] else '✗'}")
            print(f"Failed Syncs (24h): {health_status['failed_syncs_24h']}")
            
            print("\nTable Row Counts:")
            for table, count in health_status['table_counts'].items():
                status = "✓" if count >= 0 else "✗"
                print(f"  {table}: {count} {status}")
            
            print("\nSync Lag (hours):")
            for table, lag in health_status['sync_lag'].items():
                if lag == float('inf'):
                    print(f"  {table}: Never synced")
                else:
                    print(f"  {table}: {lag}h")
            
            return
        
        if args.back_propagate:
            # Update source tables with traffic data
            print("Starting back-propagation of traffic data to source tables...")
            updates_map = {
                'arribos': {'chofer': True},
                'arribos_expo_ctns': {'chofer': True}
            }
            synchronizer.update_source_tables(updates_map)
            print("Back-propagation completed")
            return
        
        if args.dry_run:
            print("DRY RUN MODE - No changes will be made")
            logger.info("Running in dry-run mode")
        
        if args.table:
            # Sync specific table
            if args.table not in synchronizer.sync_mappings:
                logger.error(f"Unknown table: {args.table}")
                sys.exit(1)
            
            if args.dry_run:
                print(f"Would sync table: {args.table} in {args.mode} mode")
                return
            
            stats = synchronizer.sync_table(args.table, full_sync=(args.mode == 'full'))
            print(f"\nSynchronization results for {args.table}:")
            print(f"Inserted: {stats['inserted']}")
            print(f"Updated: {stats['updated']}")
            print(f"Errors: {stats['errors']}")
        else:
            # Sync all tables
            if args.dry_run:
                print(f"Would sync all tables in {args.mode} mode")
                for table in synchronizer.sync_mappings.keys():
                    print(f"  - {table}")
                return
            
            if args.mode == 'full':
                overall_stats = synchronizer.run_full_sync()
            else:
                overall_stats = synchronizer.run_incremental_sync()
            
            print("\nSynchronization results:")
            total_inserted = 0
            total_updated = 0
            total_errors = 0
            
            for table, stats in overall_stats.items():
                print(f"{table}:")
                print(f"  Inserted: {stats['inserted']}")
                print(f"  Updated: {stats['updated']}")
                print(f"  Errors: {stats['errors']}")
                
                total_inserted += stats['inserted']
                total_updated += stats['updated']
                total_errors += stats['errors']
            
            print(f"\nTotal Summary:")
            print(f"  Inserted: {total_inserted}")
            print(f"  Updated: {total_updated}")
            print(f"  Errors: {total_errors}")
            
            # Recommend actions based on results
            if total_errors > 0:
                print(f"\n⚠️  {total_errors} errors detected. Check logs for details.")
            
            if total_inserted + total_updated == 0:
                print("\n✓ All data is up to date.")
            else:
                print(f"\n✓ Successfully synchronized {total_inserted + total_updated} records.")
        
        logger.info("Script execution completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
        print("\nScript interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        print(f"\nScript execution failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
