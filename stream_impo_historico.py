import streamlit as st

def show_page_impo_historico():
    # Page title
    st.title("DASSA - Operaciones de IMPO históricas")

    # Styled "Página en construcción" message
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: center; height: 70vh;">
            <div style="text-align: center;">
                <h1 style="color: #FFA500;">⚠️ Página en construcción ⚠️</h1>
                <p style="font-size: 1.2em; color: #555;">
                    Paso a paso vamos a agregar esta funcionalidad.
                </p>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )