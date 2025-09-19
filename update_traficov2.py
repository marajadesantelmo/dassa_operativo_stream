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
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from supabase_connection import (
    fetch_table_data, 
    insert_data, 
    update_data, 
    supabase_client
)

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
    
    def __init__(self):
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
    
    def prepare_record_for_sync(self, record: Dict, exclude_columns: List[str], source_id: int) -> Dict:
        """Prepare a record for insertion/update in target table"""
        cleaned_record = {}
        for key, value in record.items():
            if key not in exclude_columns:
                cleaned_record[key] = value
        
        cleaned_record['source_id'] = source_id
        cleaned_record['fecha_modificacion'] = datetime.now().isoformat()
        
        return cleaned_record
    
    def aggregate_arribos_expo_by_booking(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate arribos_expo_ctns data by booking"""
        if df.empty:
            return df
            
        # Group by booking and aggregate
        aggregated = df.groupby('Booking').agg({
            'Fecha': 'first',  # Take first date
            'Cliente': 'first',  # Take first client
            'Cantidad': 'sum',   # Sum quantities
            'Contenedor': lambda x: ', '.join(x.dropna().astype(str).unique()) if len(x.dropna()) > 0 else '-',  # Concatenate containers
            'Precinto': 'first',  # Take first precinto
            'Origen': 'first',   # Take first origin
            'Estado': 'first',   # Take first state
            'Obs.': 'first',     # Take first observation
            'Chofer': 'first',   # Take first chofer
            'id': 'first'        # Take first ID as source reference
        }).reset_index()
        
        return aggregated
    
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
        
        stats = {'inserted': 0, 'updated': 0, 'errors': 0}
        
        try:
            # Fetch source data
            logger.info(f"Fetching data from source table: {source_table}")
            source_df = fetch_table_data(source_table)
            
            if source_df.empty:
                logger.warning(f"Source table {source_table} is empty")
                return stats
            
            # Special handling for arribos_expo_ctns - aggregate by booking
            if config.get('aggregate_by_booking'):
                logger.info("Aggregating arribos_expo_ctns data by booking")
                source_df = self.aggregate_arribos_expo_by_booking(source_df)
            
            # Fetch existing target data
            logger.info(f"Fetching existing data from target table: {target_table}")
            try:
                target_df = fetch_table_data(target_table)
            except Exception as e:
                logger.warning(f"Target table {target_table} might not exist or be empty: {e}")
                target_df = pd.DataFrame()
            
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
            
            # Process each record from source
            for _, source_row in source_df.iterrows():
                try:
                    # Create composite key
                    key_values = []
                    for col in key_columns:
                        key_values.append(str(source_row.get(col, '')))
                    composite_key = '|'.join(key_values)
                    
                    source_record = source_row.to_dict()
                    source_id = source_record.get('id')
                    
                    if composite_key in existing_records:
                        # Record exists - check if update needed
                        existing_record = existing_records[composite_key]
                        
                        if self.compare_records(source_record, existing_record, exclude_columns):
                            # Update needed
                            target_record = self.prepare_record_for_sync(source_record, exclude_columns, source_id)
                            
                            result = update_data(target_table, existing_record['id'], target_record)
                            
                            self.log_sync_operation(
                                target_table, 'UPDATE', source_table, 
                                source_id, existing_record['id'],
                                {'changes_detected': True}
                            )
                            stats['updated'] += 1
                            logger.debug(f"Updated record with key: {composite_key}")
                    else:
                        # New record - insert
                        target_record = self.prepare_record_for_sync(source_record, exclude_columns, source_id)
                        
                        result = insert_data(target_table, target_record)
                        
                        # Get the inserted record ID from result
                        inserted_id = None
                        if result.data:
                            inserted_id = result.data[0].get('id')
                        
                        self.log_sync_operation(
                            target_table, 'INSERT', source_table,
                            source_id, inserted_id,
                            {'new_record': True}
                        )
                        stats['inserted'] += 1
                        logger.debug(f"Inserted new record with key: {composite_key}")
                        
                except Exception as e:
                    logger.error(f"Error processing record {composite_key}: {e}")
                    stats['errors'] += 1
                    continue
            
            logger.info(f"Sync completed for {source_table}. Stats: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error syncing table {source_table}: {e}")
            stats['errors'] += 1
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
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    synchronizer = TraficoV2Synchronizer()
    
    try:
        if args.table:
            # Sync specific table
            if args.table not in synchronizer.sync_mappings:
                logger.error(f"Unknown table: {args.table}")
                sys.exit(1)
            
            stats = synchronizer.sync_table(args.table, full_sync=(args.mode == 'full'))
            print(f"\nSynchronization results for {args.table}:")
            print(f"Inserted: {stats['inserted']}")
            print(f"Updated: {stats['updated']}")
            print(f"Errors: {stats['errors']}")
        else:
            # Sync all tables
            if args.mode == 'full':
                overall_stats = synchronizer.run_full_sync()
            else:
                overall_stats = synchronizer.run_incremental_sync()
            
            print("\nSynchronization results:")
            for table, stats in overall_stats.items():
                print(f"{table}:")
                print(f"  Inserted: {stats['inserted']}")
                print(f"  Updated: {stats['updated']}")
                print(f"  Errors: {stats['errors']}")
        
        logger.info("Script execution completed successfully")
        
    except Exception as e:
        logger.error(f"Script execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
