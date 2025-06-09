from supabase import create_client, Client
import pandas as pd
import os
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url_supabase = os.getenv("url_supabase")
key_supabase = os.getenv("url_supabase")

supabase_client = create_client(url_supabase, key_supabase)

def fetch_table_data(table_name):
    query = (
        supabase_client
        .from_(table_name)
        .select('*')
        .execute()
    )
    return pd.DataFrame(query.data)

def delete_table_data(table_name):
    # WARNING: This will delete all rows in the table
    supabase_client.from_(table_name).delete().neq('ID Pesada', None).execute()

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