#!/usr/bin/env python3
"""
Test script for Traffic Management v2 synchronization

This script tests the synchronization logic without actually writing to the database.
It simulates the sync process and validates the logic.
"""

import pandas as pd
import sys
import os
from datetime import datetime
from typing import Dict, List

# Mock data for testing
MOCK_ARRIBOS_DATA = [
    {
        'id': 1,
        'Terminal': 'Trp - Terminales 1-2-3',
        'Turno': '03:00',
        'Contenedor': 'OOCU-048760-4',
        'Cliente': 'Lift Van Int. Co S.A',
        'Booking': 'COSU6426848340',
        'Tipo CNT': 'DC',
        'Oper.': 'TD',
        'Tiempo': '05:41',
        'Estado': 'Pendiente arribo',
        'Chofer': None,
        'Dimension': '30',
        'Fecha': '19/09/2024'
    },
    {
        'id': 2,
        'Terminal': 'Exolgan',
        'Turno': '05:00',
        'Contenedor': 'UACU-824925-5',
        'Cliente': 'Mercovan Argentina S...',
        'Booking': 'HLUSAN2250701372',
        'Tipo CNT': 'DC',
        'Oper.': 'TD',
        'Tiempo': '03:41',
        'Estado': 'Pendiente arribo',
        'Chofer': None,
        'Dimension': '60',
        'Fecha': '19/09/2024'
    }
]

MOCK_PENDIENTE_DESCONSOLIDAR_DATA = [
    {
        'id': 1,
        'Contenedor': 'UACU-851282-3',
        'Cliente': 'Lift Van Int. Co S.A',
        'Entrega': 'Huxley Sa',
        'Vto. Vacio': '19/09',
        'Tipo': 'DC',
        'Peso': 3116.00,
        'Cantidad': 6,
        'Envase': 'Bultos',
        'Estado': 'Pte. Desc.',
        'Chofer': None
    },
    {
        'id': 2,
        'Contenedor': 'MSBU-457668-2',
        'Cliente': 'Lift Van Int. Co S.A',
        'Entrega': 'Exolgan',
        'Vto. Vacio': '20/09',
        'Tipo': 'DC',
        'Peso': 4996.00,
        'Cantidad': 8,
        'Envase': 'Bultos',
        'Estado': 'Vacio',
        'Chofer': None
    }
]

MOCK_REMISIONES_DATA = [
    {
        'id': 1,
        'Dia': '19/09',
        'Cliente': 'Henn Y Cia S.R.L.',
        'Booking': ': 0',
        'Contenedor': 'MRSU-319738-0',
        'Volumen': '20',
        'Precinto': 'ABC123',
        'Observaciones': 'Test',
        'Estado': 'Pendiente',
        'e-tally': '123',
        'Hora': '9:30',
        'Operacion': '38269-0-1',
        'Chofer': '-',
        'Fecha y Hora Fin': None
    },
    {
        'id': 2,
        'Dia': '19/09',
        'Cliente': 'Minera Santa Rita Sr...',
        'Booking': '25001EC03008950L',
        'Contenedor': 'MSCU-588753-2',
        'Volumen': '20',
        'Precinto': 'DEF456',
        'Observaciones': 'Test 2',
        'Estado': 'Pendiente',
        'e-tally': '124',
        'Hora': '8:00',
        'Operacion': '38237-1-1',
        'Chofer': '-',
        'Fecha y Hora Fin': None
    }
]

MOCK_ARRIBOS_EXPO_CTNS_DATA = [
    {
        'id': 1,
        'Fecha': '19/09',
        'Booking': '340500034558',
        'Cliente': 'Norfor Sa',
        'Cantidad': 3,
        'Contenedor': '-',
        'Precinto': '',
        'Origen': 'Trp - Terminales 1-2-3',
        'Estado': 'Pendiente',
        'Obs.': '28600',
        'Chofer': None
    },
    {
        'id': 2,
        'Fecha': '19/09',
        'Booking': '64179524',
        'Cliente': 'Hector Reboratti',
        'Cantidad': 1,
        'Contenedor': 'TCLU-953831-4',
        'Precinto': '**************',
        'Origen': 'Huxley Sa',
        'Estado': '16:25 Arribado',
        'Obs.': '28600',
        'Chofer': None
    },
    {
        'id': 3,
        'Fecha': '19/09',
        'Booking': '64179524',  # Same booking as above - should be aggregated
        'Cliente': 'Hector Reboratti',
        'Cantidad': 1,
        'Contenedor': 'FANU-117537-6',
        'Precinto': '**************',
        'Origen': 'Huxley Sa',
        'Estado': '16:28 Arribado',
        'Obs.': '28600',
        'Chofer': None
    }
]

class MockSynchronizer:
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
        
        # Mock data sources
        self.mock_data = {
            'arribos': MOCK_ARRIBOS_DATA,
            'pendiente_desconsolidar': MOCK_PENDIENTE_DESCONSOLIDAR_DATA,
            'remisiones': MOCK_REMISIONES_DATA,
            'arribos_expo_ctns': MOCK_ARRIBOS_EXPO_CTNS_DATA
        }
    
    def aggregate_arribos_expo_by_booking(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate arribos_expo_ctns data by booking"""
        if df.empty:
            return df
            
        # Group by booking and aggregate
        aggregated = df.groupby('Booking').agg({
            'Fecha': 'first',
            'Cliente': 'first',
            'Cantidad': 'sum',
            'Contenedor': lambda x: ', '.join(x.dropna().astype(str).unique()) if len(x.dropna()) > 0 else '-',
            'Precinto': 'first',
            'Origen': 'first',
            'Estado': 'first',
            'Obs.': 'first',
            'Chofer': 'first',
            'id': 'first'
        }).reset_index()
        
        return aggregated
    
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
    
    def test_key_generation(self, source_table: str) -> None:
        """Test key generation logic"""
        print(f"\n=== Testing key generation for {source_table} ===")
        
        config = self.sync_mappings[source_table]
        key_columns = config['key_columns']
        data = self.mock_data[source_table]
        
        df = pd.DataFrame(data)
        
        # Special handling for arribos_expo_ctns
        if config.get('aggregate_by_booking'):
            print("Aggregating by booking...")
            df = self.aggregate_arribos_expo_by_booking(df)
        
        print(f"Key columns: {key_columns}")
        
        for _, row in df.iterrows():
            key_values = []
            for col in key_columns:
                key_values.append(str(row.get(col, '')))
            composite_key = '|'.join(key_values)
            print(f"Record ID {row.get('id', 'N/A')}: Key = '{composite_key}'")
    
    def test_record_preparation(self, source_table: str) -> None:
        """Test record preparation logic"""
        print(f"\n=== Testing record preparation for {source_table} ===")
        
        config = self.sync_mappings[source_table]
        exclude_columns = config['exclude_columns']
        data = self.mock_data[source_table]
        
        df = pd.DataFrame(data)
        
        # Take first record for testing
        if not df.empty:
            source_record = df.iloc[0].to_dict()
            source_id = source_record.get('id')
            
            prepared_record = self.prepare_record_for_sync(source_record, exclude_columns, source_id)
            
            print(f"Original record keys: {list(source_record.keys())}")
            print(f"Prepared record keys: {list(prepared_record.keys())}")
            print(f"Excluded columns: {exclude_columns}")
            print(f"Source ID: {source_id}")
            
            # Verify exclusions worked
            for col in exclude_columns:
                if col in prepared_record:
                    print(f"ERROR: Column '{col}' should have been excluded!")
                else:
                    print(f"✓ Column '{col}' correctly excluded")
    
    def test_aggregation(self) -> None:
        """Test aggregation logic for arribos_expo_ctns"""
        print(f"\n=== Testing aggregation for arribos_expo_ctns ===")
        
        df = pd.DataFrame(MOCK_ARRIBOS_EXPO_CTNS_DATA)
        print(f"Original data shape: {df.shape}")
        print("Original data:")
        print(df[['Booking', 'Cliente', 'Cantidad', 'Contenedor']].to_string())
        
        aggregated = self.aggregate_arribos_expo_by_booking(df)
        print(f"\nAggregated data shape: {aggregated.shape}")
        print("Aggregated data:")
        print(aggregated[['Booking', 'Cliente', 'Cantidad', 'Contenedor']].to_string())
        
        # Verify aggregation worked correctly
        booking_64179524_original = df[df['Booking'] == '64179524']['Cantidad'].sum()
        booking_64179524_aggregated = aggregated[aggregated['Booking'] == '64179524']['Cantidad'].iloc[0]
        
        if booking_64179524_original == booking_64179524_aggregated:
            print(f"✓ Quantity aggregation correct: {booking_64179524_original}")
        else:
            print(f"ERROR: Quantity aggregation failed! Original: {booking_64179524_original}, Aggregated: {booking_64179524_aggregated}")
    
    def run_all_tests(self) -> None:
        """Run all test cases"""
        print("Starting Traffic Management v2 Synchronization Tests")
        print("=" * 60)
        
        # Test key generation for all tables
        for source_table in self.sync_mappings.keys():
            self.test_key_generation(source_table)
        
        # Test record preparation for all tables
        for source_table in self.sync_mappings.keys():
            self.test_record_preparation(source_table)
        
        # Test aggregation
        self.test_aggregation()
        
        print("\n" + "=" * 60)
        print("All tests completed!")

def main():
    """Run the tests"""
    tester = MockSynchronizer()
    tester.run_all_tests()

if __name__ == "__main__":
    main()