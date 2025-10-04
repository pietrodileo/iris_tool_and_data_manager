# ui/explore_tab.py
"""
Explore Tab UI Component
Main tab for exploring and analyzing IRIS tables
"""

import streamlit as st
from utils.iristool import IRIStool
from utils.session_state import reset_table_data
from ui.explore_components.data_view import render_data_view
from ui.explore_components.data_profile import render_data_profile
from ui.explore_components.transform import render_transform
from ui.explore_components.visualize import render_visualize
from ui.explore_components.sql_generation import render_sql_generation

def render_explore_tab(iris: IRIStool):
    """Render the explore and analyze tab"""
    
    st.subheader("🔍 Explore IRIS Tables")
    
    try:
        # Schema and table selection
        schema_input, selected_table = _render_table_selector(iris)
        
        if selected_table != "(none)":
            # Load data section
            _render_load_data_section(iris, schema_input, selected_table)
            
            # Analysis sections (only if data is loaded)
            if st.session_state.table_data is not None and not st.session_state.table_data.empty:
                _render_analysis_sections()
    
    except Exception as e:
        st.error(f"❌ Error: {e}")
        st.exception(e)

def _render_table_selector(iris: IRIStool):
    """Render schema and table selection dropdowns"""
    
    # Get schemas
    schemas = iris.show_namespace_schemas()
    schemas_list = [row['TABLE_SCHEMA'] for _, row in schemas.iterrows()]

    default_schema_index = (
        schemas_list.index(st.session_state.schema_input) + 1
        if st.session_state.schema_input in schemas_list
        else 0
    )
    
    schema_input = st.selectbox(
        "📁 Schema",
        options=["(none)"] + schemas_list,
        index=default_schema_index,
        key="schema_select_widget"
    )
    
    # Update session state
    if schema_input != st.session_state.schema_input:
        st.session_state.schema_input = schema_input
        reset_table_data()

    selected_table = "(none)"
    
    if schema_input != "(none)":
        # Get tables for selected schema
        tables = iris.show_namespace_tables(table_schema=schema_input)
        tables_list = [row['TABLE_NAME'] for _, row in tables.iterrows()]

        default_table_index = (
            tables_list.index(st.session_state.selected_table) + 1
            if st.session_state.selected_table in tables_list
            else 0
        )
        
        selected_table = st.selectbox(
            "📊 Table",
            options=["(none)"] + tables_list,
            index=default_table_index,
            key="table_select_widget"
        )
        
        # Update session state
        if selected_table != st.session_state.selected_table:
            st.session_state.selected_table = selected_table
            reset_table_data()
    
    return schema_input, selected_table

def _render_load_data_section(iris: IRIStool, schema: str, table: str):
    """Render data loading section"""
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        num_rows = st.number_input(
            "Number of rows to load",
            min_value=1,
            max_value=10000,
            value=st.session_state.explorer_num_rows,
            key="explorer_num_rows",
            help="Maximum number of rows to load from the table"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        load_button = st.button("📊 Load Data", type="primary", width='stretch')
    
    if load_button:
        _load_table_data(iris, schema, table, num_rows)

def _load_table_data(iris: IRIStool, schema: str, table: str, num_rows: int):
    """Load data from selected table"""
    with st.spinner("Loading data..."):
        try:
            sql = f"SELECT TOP {num_rows} * FROM {schema}.{table}"
            st.session_state.table_data = iris.fetch(sql)
            st.session_state.filters = {}
            st.session_state.transformed_data = None
            st.success(f"✅ Loaded {len(st.session_state.table_data)} rows from {schema}.{table}")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            st.exception(e)

def _render_analysis_sections():
    """Render analysis sub-tabs"""
    
    result = st.session_state.table_data
    
    if result.empty:
        st.warning("⚠️ Table is empty")
        return
    
    # Create sub-tabs for different analysis views
    analysis_tabs = st.tabs([
        "📋 Data View", 
        "📊 Data Profile", 
        "🔧 Transform", 
        "📈 Visualize",
        "🤖 Text to SQL"
    ])
    
    with analysis_tabs[0]:
        render_data_view(result)
    
    with analysis_tabs[1]:
        render_data_profile(result)
    
    with analysis_tabs[2]:
        render_transform(result)
    
    with analysis_tabs[3]:
        render_visualize(result)
        
    with analysis_tabs[4]:
        render_sql_generation()