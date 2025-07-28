import streamlit as st
import pandas as pd
from supabase_connection import fetch_table_data, insert_data, delete_data

def show_page_usuarios():
    st.title("Gestión de Usuarios")
    
    # Fetch current users
    users_df = fetch_table_data("users")
    
    # Display current users
    st.subheader("Usuarios Actuales")
    
    # Create a display dataframe without the id column for better UX
    display_df = users_df[['user', 'clave', 'clientes']].copy()
    st.dataframe(display_df, use_container_width=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Agregar Usuario")
        with st.form("add_user_form"):
            new_user = st.text_input("Nombre de Usuario")
            new_password = st.text_input("Contraseña", type="password")
            new_clientes = st.number_input("Clientes", min_value=0, value=0)
            
            if st.form_submit_button("Agregar Usuario"):
                if new_user and new_password:
                    # Check if user already exists
                    if new_user in users_df['user'].values:
                        st.error("El usuario ya existe")
                    else:
                        # Insert new user - explicitly create clean data without any id
                        new_user_data = {
                            'user': str(new_user).strip(),
                            'clave': str(new_password).strip(),
                            'clientes': int(new_clientes)
                        }
                        try:
                            insert_data("users", new_user_data)
                            st.success(f"Usuario '{new_user}' agregado exitosamente")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al agregar usuario: {str(e)}")
                else:
                    st.error("Por favor complete todos los campos obligatorios")
    
    with col2:
        st.subheader("Eliminar Usuario")
        if len(users_df) > 0:
            user_to_delete = st.selectbox(
                "Seleccionar usuario a eliminar",
                users_df['user'].tolist(),
                key="delete_user_select"
            )
            
            if st.button("Eliminar Usuario", type="secondary"):
                if user_to_delete:
                    # Get user ID for deletion
                    user_id = users_df[users_df['user'] == user_to_delete]['id'].iloc[0]
                    
                    try:
                        delete_data("users", user_id)
                        st.success(f"Usuario '{user_to_delete}' eliminado exitosamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al eliminar usuario: {str(e)}")
        else:
            st.info("No hay usuarios para eliminar")
    
    with col3:
        # Third column - can be used for additional functionality
        st.write("")  # Empty space for now