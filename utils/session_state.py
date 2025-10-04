# utils/session_state.py
"""
Session State Management
Initialize and manage Streamlit session state variables
"""

import streamlit as st
from typing import Any
from config.settings import AppConfig

def initialize_session_state(config: AppConfig):
    """Initialize all session state variables with default values"""
    
    defaults = {
        # Connection state
        "iris_connection": None,
        "connection_status": "Not Connected",
        "use_default_connection": True,
        
        # Upload tab
        "df": None,
        
        # Explore tab
        "schema_input": "(none)",
        "selected_table": "(none)",
        "explorer_num_rows": 100,
        "table_data": None,
        
        # Filtering and transformation
        "filters": {},
        "transformed_data": None,
        
        # UI state
        "active_tab": 0,
        
        # ollama api url
        "ollama_api_url": config.OLLAMA_API_URL,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def reset_table_data():
    """Reset table data and related state when switching tables"""
    st.session_state.table_data = None
    st.session_state.filters = {}
    st.session_state.transformed_data = None

def reset_connection_data():
    """Reset all data when disconnecting"""
    st.session_state.table_data = None
    st.session_state.filters = {}
    st.session_state.transformed_data = None
    st.session_state.df = None
    st.session_state.schema_input = "(none)"
    st.session_state.selected_table = "(none)"

def set_session_value(key: str, value: Any):
    """Set a session state value"""
    st.session_state[key] = value

def get_session_value(key: str, default: Any = None) -> Any:
    """Get a session state value with optional default"""
    return st.session_state.get(key, default)