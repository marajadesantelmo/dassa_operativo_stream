#!/usr/bin/env python3
"""
Mock version of the Traffic Management v2 Update Script for testing

This script mocks the functionality to test argument parsing and basic logic
without requiring database connections.
"""

import pandas as pd
import sys
from datetime import datetime
import json
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MockTraficoV2Synchronizer:
    """Mock version of TraficoV2Synchronizer for testing"""
    
    def __init__(self):
        self.sync_mappings = {
            'arribos': {
                'target': 'traficov2_arribos',
                'key_columns': ['Contenedor'],
                'exclude_columns': ['id']
            },
            'pendiente_desconsolidar': {
                'target': 'traficov2_pendiente_desconsolidar', 
                'key_columns': ['Contenedor'],
                'exclude_columns': ['id']
            },
            'remisiones': {
                'target': 'traficov2_remisiones',
                'key_columns': ['Contenedor', 'Operacion'],
                'exclude_columns': ['id']
            },
            'arribos_expo_ctns': {
                'target': 'traficov2_arribos_ctns_expo',
                'key_columns': ['Booking'],
                'exclude_columns': ['id'],
                'aggregate_by_booking': True
            }
        }
        
    def sync_table(self, source_table: str, full_sync: bool = False) -> Dict[str, int]:
        """Mock sync of a source table to its corresponding target table"""
        logger.info(f"Mock sync for table: {source_table} (full_sync={full_sync})")
        
        # Simulate some work with realistic stats
        import time
        time.sleep(0.1)  # Simulate processing time
        
        # Return mock statistics
        if source_table == 'arribos':
            return {'inserted': 15, 'updated': 3, 'errors': 0}
        elif source_table == 'pendiente_desconsolidar':
            return {'inserted': 22, 'updated': 1, 'errors': 0}
        elif source_table == 'remisiones':
            return {'inserted': 34, 'updated': 5, 'errors': 0}
        elif source_table == 'arribos_expo_ctns':
            return {'inserted': 9, 'updated': 2, 'errors': 0}  # Less due to aggregation
        else:
            return {'inserted': 0, 'updated': 0, 'errors': 1}
    
    def run_full_sync(self) -> Dict[str, Dict[str, int]]:
        """Mock full synchronization of all tables"""
        logger.info("Starting mock full synchronization of all traffic v2 tables")
        
        overall_stats = {}
        
        for source_table in self.sync_mappings.keys():
            stats = self.sync_table(source_table, full_sync=True)
            overall_stats[source_table] = stats
        
        logger.info("Mock full synchronization completed")
        logger.info(f"Overall stats: {overall_stats}")
        
        return overall_stats
    
    def run_incremental_sync(self) -> Dict[str, Dict[str, int]]:
        """Mock incremental synchronization"""
        logger.info("Starting mock incremental synchronization")
        
        overall_stats = {}
        
        for source_table in self.sync_mappings.keys():
            # Simulate that some tables have been synced before
            has_previous_sync = source_table in ['arribos', 'remisiones']
            stats = self.sync_table(source_table, full_sync=not has_previous_sync)
            overall_stats[source_table] = stats
        
        logger.info("Mock incremental synchronization completed")
        logger.info(f"Overall stats: {overall_stats}")
        
        return overall_stats


def main():
    """Main function to run the mock synchronization"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Traffic Management v2 Synchronization Script (Mock Version)')
    parser.add_argument('--mode', choices=['full', 'incremental'], default='incremental',
                       help='Synchronization mode (default: incremental)')
    parser.add_argument('--table', help='Sync specific table only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    synchronizer = MockTraficoV2Synchronizer()
    
    try:
        if args.table:
            # Sync specific table
            if args.table not in synchronizer.sync_mappings:
                logger.error(f"Unknown table: {args.table}")
                logger.info(f"Available tables: {list(synchronizer.sync_mappings.keys())}")
                sys.exit(1)
            
            stats = synchronizer.sync_table(args.table, full_sync=(args.mode == 'full'))
            print(f"\nMock synchronization results for {args.table}:")
            print(f"Inserted: {stats['inserted']}")
            print(f"Updated: {stats['updated']}")
            print(f"Errors: {stats['errors']}")
        else:
            # Sync all tables
            if args.mode == 'full':
                overall_stats = synchronizer.run_full_sync()
            else:
                overall_stats = synchronizer.run_incremental_sync()
            
            print("\nMock synchronization results:")
            for table, stats in overall_stats.items():
                print(f"{table}:")
                print(f"  Inserted: {stats['inserted']}")
                print(f"  Updated: {stats['updated']}")
                print(f"  Errors: {stats['errors']}")
        
        logger.info("Mock script execution completed successfully")
        
    except Exception as e:
        logger.error(f"Mock script execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()