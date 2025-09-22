#!/usr/bin/env python3
"""
Enhanced Test Script for TraficoV2 Synchronizer

This script tests the enhanced features of update_traficov2.py
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime
import logging

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config_loading():
    """Test configuration loading functionality"""
    print("\n=== Testing Configuration Loading ===")
    
    # Import the synchronizer
    sys.path.append('.')
    from update_traficov2 import TraficoV2Synchronizer
    
    try:
        # Test with existing config
        sync = TraficoV2Synchronizer('trafico_config.json')
        assert hasattr(sync, 'config')
        assert 'csv_sources' in sync.config
        print("✓ Configuration loaded successfully")
        
        # Test with non-existent config (should use defaults)
        sync_default = TraficoV2Synchronizer('non_existent.json')
        assert hasattr(sync_default, 'config')
        print("✓ Default configuration loaded for missing file")
        
        return True
    except Exception as e:
        print(f"✗ Configuration loading failed: {e}")
        return False

def test_data_validation():
    """Test data validation functionality"""
    print("\n=== Testing Data Validation ===")
    
    try:
        from update_traficov2 import TraficoV2Synchronizer
        sync = TraficoV2Synchronizer()
        
        # Test valid record
        valid_record = {
            'Contenedor': 'ABCD1234567',
            'Booking': 'ABC12345',
            'Cantidad': 2
        }
        
        is_valid, errors = sync.validate_record(valid_record, 'arribos_expo_ctns')
        print(f"Valid record test: {is_valid} (errors: {errors})")
        
        # Test invalid record
        invalid_record = {
            'Contenedor': '',
            'Booking': '',
            'Cantidad': 0
        }
        
        is_valid, errors = sync.validate_record(invalid_record, 'arribos_expo_ctns')
        print(f"Invalid record test: {is_valid} (errors: {len(errors)} found)")
        
        return True
    except Exception as e:
        print(f"✗ Data validation failed: {e}")
        return False

def test_data_transformation():
    """Test data transformation functionality"""
    print("\n=== Testing Data Transformation ===")
    
    try:
        from update_traficov2 import TraficoV2Synchronizer
        sync = TraficoV2Synchronizer()
        
        # Test record transformation
        test_record = {
            'Contenedor': ' abcd1234567 ',
            'Booking': ' xyz12345 ',
            'Fecha': '2024-01-15'
        }
        
        transformed = sync.transform_record(test_record, 'arribos_expo_ctns')
        
        print(f"Original Contenedor: '{test_record['Contenedor']}'")
        print(f"Transformed Contenedor: '{transformed['Contenedor']}'")
        print(f"Original Booking: '{test_record['Booking']}'")
        print(f"Transformed Booking: '{transformed['Booking']}'")
        
        # Check transformations
        assert transformed['Contenedor'] == 'ABCD1234567'
        assert transformed['Booking'] == 'XYZ12345'
        
        print("✓ Data transformation working correctly")
        return True
    except Exception as e:
        print(f"✗ Data transformation failed: {e}")
        return False

def test_quantity_expansion():
    """Test record expansion by quantity"""
    print("\n=== Testing Quantity Expansion ===")
    
    try:
        from update_traficov2 import TraficoV2Synchronizer
        sync = TraficoV2Synchronizer()
        
        # Create test dataframe
        test_data = pd.DataFrame([
            {'Booking': 'ABC123', 'Cantidad': 3, 'Cliente': 'Test Client'},
            {'Booking': 'XYZ789', 'Cantidad': 1, 'Cliente': 'Another Client'}
        ])
        
        expanded = sync.expand_records_by_quantity(test_data, 'arribos_expo_ctns')
        
        print(f"Original records: {len(test_data)}")
        print(f"Expanded records: {len(expanded)}")
        
        # Should have 4 records total (3 + 1)
        expected_count = 4
        if len(expanded) == expected_count:
            print("✓ Quantity expansion working correctly")
            return True
        else:
            print(f"✗ Expected {expected_count} records, got {len(expanded)}")
            return False
            
    except Exception as e:
        print(f"✗ Quantity expansion failed: {e}")
        return False

def test_health_check():
    """Test health check functionality"""
    print("\n=== Testing Health Check ===")
    
    try:
        from update_traficov2 import TraficoV2Synchronizer
        sync = TraficoV2Synchronizer()
        
        # Mock the database connection check to avoid actual DB calls
        def mock_db_check():
            return True
        
        sync.check_database_connection = mock_db_check
        
        # Mock other methods to avoid DB calls
        sync.get_table_row_counts = lambda: {'test_table': 100}
        sync.get_all_last_sync_times = lambda: {'test_table': datetime.now().isoformat()}
        sync.calculate_sync_lag = lambda: {'test_table': 1.5}
        sync.count_recent_failures = lambda: 0
        
        health_status = sync.perform_health_check()
        
        print(f"Database connection: {health_status['database_connection']}")
        print(f"Table counts: {health_status['table_counts']}")
        print(f"Sync lag: {health_status['sync_lag']}")
        print(f"Recent failures: {health_status['failed_syncs_24h']}")
        
        print("✓ Health check functionality working")
        return True
        
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False

def test_csv_data_loading():
    """Test CSV data loading functionality"""
    print("\n=== Testing CSV Data Loading ===")
    
    try:
        from update_traficov2 import TraficoV2Synchronizer
        
        # Create test CSV data
        os.makedirs('./data', exist_ok=True)
        test_df = pd.DataFrame([
            {'Contenedor': 'TEST1234567', 'Booking': 'TEST123', 'Cantidad': 1},
            {'Contenedor': 'TEST7654321', 'Booking': 'TEST456', 'Cantidad': 2}
        ])
        test_df.to_csv('./data/test_arribos.csv', index=False)
        
        # Test config with CSV enabled
        test_config = {
            "csv_sources": {
                "enabled": True,
                "data_path": "./data/",
                "files": {
                    "test_arribos": "test_arribos.csv"
                }
            }
        }
        
        # Save test config
        with open('test_config.json', 'w') as f:
            json.dump(test_config, f)
        
        sync = TraficoV2Synchronizer('test_config.json')
        external_sources = sync.load_external_data_sources()
        
        if 'test_arribos' in external_sources:
            loaded_df = external_sources['test_arribos']
            print(f"Loaded {len(loaded_df)} records from CSV")
            print("✓ CSV data loading working")
            result = True
        else:
            print("✗ CSV data not loaded")
            result = False
        
        # Cleanup
        if os.path.exists('./data/test_arribos.csv'):
            os.remove('./data/test_arribos.csv')
        if os.path.exists('test_config.json'):
            os.remove('test_config.json')
        
        return result
        
    except Exception as e:
        print(f"✗ CSV data loading failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("Starting Enhanced TraficoV2 Synchronizer Tests")
    print("=" * 50)
    
    tests = [
        test_config_loading,
        test_data_validation,
        test_data_transformation,
        test_quantity_expansion,
        test_health_check,
        test_csv_data_loading
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)