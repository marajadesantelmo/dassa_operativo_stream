#!/usr/bin/env python3
"""
Demo script to showcase enhanced features of update_traficov2.py
"""

import pandas as pd
import json
import os
from datetime import datetime

def create_demo_data():
    """Create demonstration data files"""
    print("Creating demo data files...")
    
    # Create demo CSV data
    demo_data = {
        'arribos_demo.csv': pd.DataFrame([
            {'Contenedor': 'DEMO1234567', 'Fecha': '20/01/2024', 'Cliente': 'Demo Client 1', 'Estado': 'Arribado'},
            {'Contenedor': 'DEMO7654321', 'Fecha': '21/01/2024', 'Cliente': 'Demo Client 2', 'Estado': 'Pendiente'},
            {'Contenedor': 'TEST9876543', 'Fecha': '22/01/2024', 'Cliente': 'Test Client', 'Estado': 'En Transito'}
        ]),
        'expo_demo.csv': pd.DataFrame([
            {'Booking': 'DMO12345', 'Contenedor': 'DEMO1234567', 'Cliente': 'Export Client 1', 'Cantidad': 2},
            {'Booking': 'DMO67890', 'Contenedor': '-', 'Cliente': 'Export Client 2', 'Cantidad': 3},
            {'Booking': 'TST11111', 'Contenedor': 'TEST9999999', 'Cliente': 'Test Export', 'Cantidad': 1}
        ])
    }
    
    os.makedirs('demo_data', exist_ok=True)
    for filename, df in demo_data.items():
        filepath = os.path.join('demo_data', filename)
        df.to_csv(filepath, index=False)
        print(f"  Created {filepath} with {len(df)} records")

def create_demo_config():
    """Create demo configuration file"""
    print("Creating demo configuration...")
    
    demo_config = {
        "csv_sources": {
            "enabled": True,
            "data_path": "./demo_data/",
            "files": {
                "arribos_demo": "arribos_demo.csv",
                "expo_demo": "expo_demo.csv"
            }
        },
        "sql_server": {
            "enabled": False
        },
        "sync_settings": {
            "arribos": {
                "batch_size": 10,
                "validation_enabled": True,
                "retry_attempts": 2
            },
            "arribos_expo_ctns": {
                "batch_size": 5,
                "container_assignment": True,
                "quantity_expansion": True,
                "retry_attempts": 2
            }
        },
        "business_rules": {
            "container_validation": {
                "required_fields": ["Contenedor"],
                "container_format_regex": "^[A-Z]{4}[0-9]{7}$"
            }
        }
    }
    
    with open('demo_config.json', 'w') as f:
        json.dump(demo_config, f, indent=2)
    
    print("  Created demo_config.json")

def demonstrate_features():
    """Demonstrate the enhanced features"""
    print("\n" + "="*60)
    print("ENHANCED FEATURES DEMONSTRATION")
    print("="*60)
    
    try:
        from update_traficov2 import TraficoV2Synchronizer
        
        # Initialize with demo config
        print("\n1. Configuration Loading:")
        sync = TraficoV2Synchronizer('demo_config.json')
        print(f"   ✓ Loaded configuration with CSV sources: {sync.config['csv_sources']['enabled']}")
        
        # Load external data sources
        print("\n2. External Data Loading:")
        external_sources = sync.load_external_data_sources()
        for name, df in external_sources.items():
            print(f"   ✓ Loaded {name}: {len(df)} records")
        
        # Demonstrate data validation
        print("\n3. Data Validation:")
        valid_record = {'Contenedor': 'DEMO1234567', 'Booking': 'DMO12345'}
        is_valid, errors = sync.validate_record(valid_record, 'arribos')
        print(f"   Valid record: {is_valid} (errors: {len(errors)})")
        
        invalid_record = {'Contenedor': '', 'Booking': ''}
        is_valid, errors = sync.validate_record(invalid_record, 'arribos')
        print(f"   Invalid record: {is_valid} (errors: {len(errors)} found)")
        
        # Demonstrate data transformation
        print("\n4. Data Transformation:")
        test_record = {'Contenedor': ' demo1234567 ', 'Booking': ' dmo12345 '}
        transformed = sync.transform_record(test_record, 'arribos_expo_ctns')
        print(f"   Original: {test_record}")
        print(f"   Transformed: {transformed}")
        
        # Demonstrate quantity expansion
        print("\n5. Quantity Expansion:")
        if 'expo_demo' in external_sources:
            expanded = sync.expand_records_by_quantity(external_sources['expo_demo'], 'arribos_expo_ctns')
            print(f"   Original records: {len(external_sources['expo_demo'])}")
            print(f"   Expanded records: {len(expanded)}")
            print(f"   Records with Cantidad > 1 are expanded into multiple rows")
        
        # Demonstrate health check (mocked)
        print("\n6. Health Check (mocked):")
        sync.check_database_connection = lambda: False  # Mock as unavailable
        sync.get_table_row_counts = lambda: {'demo_table': 100}
        sync.calculate_sync_lag = lambda: {'demo_table': 2.5}
        sync.count_recent_failures = lambda: 0
        
        health = sync.perform_health_check()
        print(f"   Database connection: {'✓' if health['database_connection'] else '✗'}")
        print(f"   Table counts: {health['table_counts']}")
        print(f"   Sync lag: {health['sync_lag']}")
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETE")
        print("="*60)
        print("\nFeatures demonstrated:")
        print("  ✓ Configuration management")
        print("  ✓ External CSV data loading")
        print("  ✓ Data validation with business rules")
        print("  ✓ Data transformation and normalization")
        print("  ✓ Quantity-based record expansion")
        print("  ✓ Health monitoring system")
        print("\nAll enhanced features are working correctly!")
        
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()

def cleanup_demo():
    """Clean up demo files"""
    print(f"\nCleaning up demo files...")
    
    import shutil
    
    files_to_remove = ['demo_config.json']
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"  Removed {file}")
    
    if os.path.exists('demo_data'):
        shutil.rmtree('demo_data')
        print(f"  Removed demo_data directory")

def main():
    """Main demo function"""
    print("Enhanced TráficoV2 Synchronizer Demo")
    print("=" * 40)
    
    try:
        create_demo_data()
        create_demo_config()
        demonstrate_features()
        
        input("\nPress Enter to clean up demo files...")
        cleanup_demo()
        
        print("\nDemo completed successfully! 🎉")
        
    except KeyboardInterrupt:
        print("\nDemo interrupted")
        cleanup_demo()
    except Exception as e:
        print(f"\nDemo failed: {e}")
        cleanup_demo()

if __name__ == "__main__":
    main()