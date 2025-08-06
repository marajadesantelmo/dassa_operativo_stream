from supabase import create_client, Client
import pandas as pd
import os
from datetime import datetime
from supabase import create_client, Client
import time

url_supabase = os.getenv("url_supabase")
key_supabase= os.getenv("key_supabase")

supabase_client = create_client(url_supabase, key_supabase)

def fetch_table_data(table_name, retries=3, delay=5):
    for attempt in range(retries):
        try:
            query = (
                supabase_client
                .from_(table_name)
                .select('*')
                .execute()
            )
            return pd.DataFrame(query.data)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise

def delete_table_data(table_name):
    # WARNING: This will delete all rows in the table
    supabase_client.from_(table_name).delete().neq('ID Pesada', None).execute()

def delete_table_data_estado(table_name):
    # WARNING: This will delete all rows in the table
    supabase_client.from_(table_name).delete().neq('Estado', None).execute()

def delete_table_data_contenedor(table_name):
    # WARNING: This will delete all rows in the table
    supabase_client.from_(table_name).delete().neq('Contenedor', None).execute()

def delete_table_data_cliente(table_name):
    # WARNING: This will delete all rows in the table
    supabase_client.from_(table_name).delete().neq('cliente_mercaderia', None).execute()

def insert_table_data(table_name, data):
    for record in data:
        try:
            supabase_client.from_(table_name).insert(record).execute()
        except APIError as e:
            if 'duplicate key value violates unique constraint' in str(e):
                supabase_client.from_(table_name).upsert(record).execute()
            else:
                raise e

def update_log(table_name):
    log_entry = {
        "table_name": table_name,
        "last_update": datetime.now().isoformat()
    }
    supabase_client.from_("update_log").insert(log_entry).execute()

def insert_data(table_name, data):
    """Insert a single record into the specified table"""
    try:
        # Remove 'id' field if it exists to let Supabase auto-generate it
        clean_data = {k: v for k, v in data.items() if k != 'id'}
        result = supabase_client.from_(table_name).insert(clean_data).execute()
        return result
    except Exception as e:
        raise e

def delete_data(table_name, record_id):
    """Delete a record by ID from the specified table"""
    try:
        result = supabase_client.from_(table_name).delete().eq('id', record_id).execute()
        return result
    except Exception as e:
        raise e

def update_data(table_name, record_id, data):
    """Update a record by ID in the specified table"""
    try:
        # Remove 'id' field if it exists to avoid conflicts
        clean_data = {k: v for k, v in data.items() if k != 'id'}
        result = supabase_client.from_(table_name).update(clean_data).eq('id', record_id).execute()
        return result
    except Exception as e:
        raise e

def update_data_by_key(table_name, key_column, key_value, data):
    """Update a record by using a specific column as identifier"""
    try:
        clean_data = {k: v for k, v in data.items() if k != 'id'}
        result = supabase_client.from_(table_name).update(clean_data).eq(key_column, key_value).execute()
        return result
    except Exception as e:
        raise e

def update_data_by_index(table_name, row_index, data, identifier_column='Contenedor'):
    """Update a record by using a specific column as identifier for tables without id"""
    try:
        # Get the current data to find the identifier value
        current_data = fetch_table_data(table_name)
        if row_index < len(current_data):
            identifier_value = current_data.iloc[row_index][identifier_column]
            clean_data = {k: v for k, v in data.items() if k != 'id'}
            result = supabase_client.from_(table_name).update(clean_data).eq(identifier_column, identifier_value).execute()
            return result
        else:
            raise Exception(f"Row index {row_index} out of range for table {table_name}")
    except Exception as e:
        raise e