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
        
        # transformation results
        "aggregation_result": None,

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
    st.session_state.aggregation_result = None

def reset_connection_data():
    """Reset all data when disconnecting"""
    st.session_state.table_data = None
    st.session_state.filters = {}
    st.session_state.transformed_data = None
    st.session_state.aggregation_result = None
    st.session_state.df = None
    st.session_state.schema_input = "(none)"
    st.session_state.selected_table = "(none)"

def clear_all_transformations():
    """Clear all independent transformation results"""
    st.session_state.aggregation_result = None

def set_session_value(key: str, value: Any):
    """Set a session state value"""
    st.session_state[key] = value

def get_session_value(key: str, default: Any = None) -> Any:
    """Get a session state value with optional default"""
    return st.session_state.get(key, default)

def get_working_dataframe() -> Any:
    """
    Get the current working dataframe based on priority:
    1. Transformed data (if exists)
    2. Filtered table data (if exists)
    3. Original table data
    
    Note: This does NOT include aggregation results as they are isolated
    """
    if st.session_state.get('transformed_data') is not None:
        return st.session_state.transformed_data
    
    return st.session_state.get('table_data')

def has_aggregation_result() -> bool:
    """Check if there's an active aggregation result"""
    return st.session_state.get('aggregation_result') is not None

def get_aggregation_result() -> dict:
    """
    Get the isolated aggregation result
    
    Returns:
        dict with keys: 'data', 'group_cols', 'agg_col', 'agg_func'
        or None if no aggregation exists
    """
    return st.session_state.get('aggregation_result')

def clear_all_analysis():
    """Clear all analysis results (filters, transformations, and aggregations)"""
    st.session_state.filters = {}
    st.session_state.aggregation_result = None