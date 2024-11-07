import streamlit as st
import stream_impo
import stream_expo
import stream_impo_historico
import stream_expo_historico

# Page configuration
st.set_page_config(page_title="Operativa DASSA", 
                   page_icon="📊", 
                   layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
        /* Solarized Dark background and text colors */
        body {
            background-color: #002b36;
            color: #839496;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #93a1a1;
        }
        .stApp {
            background-color: #002b36;
        }
        
        /* Table customization */
        .dataframe {
            background-color: #D3D3D3;
            color: black;
        }
        .dataframe table {
            width: auto;
            table-layout: auto;
            background-color: #D3D3D3;
        }
        .dataframe th {
            background-color: #B0B0B0;
            color: black;
            font-weight: bold;
            font-size: 10px;
        }
        .dataframe td {
            background-color: #D3D3D3;
            color: black;
            font-size: 6px;
        }
        .dataframe td, .dataframe th {
            padding: 0.1rem;
            text-align: left;
            word-wrap: break-word;
            white-space: nowrap;
            border: 1px solid #586e75;
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #073642;
            color: #839496;
            font-size: 8px;
            width: 20px;
        }
        
        /* Streamlit buttons and input fields */
        .stButton button, .stTextInput input {
            background-color: #073642;
            color: #93a1a1;
            border: 1px solid #586e75;
        }
        .stButton button:hover {
            background-color: #586e75;
        }

        /* Radio button customization */
        .stRadio > label {
            color: white;
            font-size: 20px;  /* Larger font size for radio button labels */
        }
        .stRadio > div div label {
            font-size: 24px; /* Increase font size for "IMPO" and "EXPO" */
            font-weight: bold; /* Bold text for better emphasis */
        }
    </style>
    """, 
    unsafe_allow_html=True
)

# JavaScript for automatic refresh every 10 seconds
refresh_interval = 10  # Refresh interval in seconds
st.markdown(
    f"""
    <script>
    function reload() {{
        setTimeout(function() {{
            window.location.reload(1);
        }}, {refresh_interval * 1000});
    }}
    reload();
    </script>
    """,
    unsafe_allow_html=True
)

# Top Navigation
page_selection = st.radio("", ["IMPO", "EXPO"])

# Load the appropriate page based on sidebar selection
if page_selection == "IMPO":
    stream_impo.show_page_impo()  # Function to render the IMPO page
elif page_selection == "EXPO":
    stream_expo.show_page_expo()  # Function to render the EXPO page
