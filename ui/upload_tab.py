# ui/upload_tab.py
"""
Upload Tab UI Component
Handles file upload, preview, and saving to IRIS database
"""

import streamlit as st
import pandas as pd
from typing import Optional
from utils.iristool import IRIStool

def render_upload_tab(iris: IRIStool):
    """Render the upload data tab"""
    
    uploaded_file = st.file_uploader(
        "Upload a file (CSV, Excel (XLSX) or JSON )",
        type=["csv", "xlsx", "xls", "json"]
    )

    if uploaded_file is not None:
        _process_uploaded_file(uploaded_file)
        
        if st.session_state.df is not None:
            _render_preview_section()
            _render_indices_section()
            _render_save_section(iris)

def _process_uploaded_file(uploaded_file):
    """Process and load uploaded file into DataFrame"""
    filename = uploaded_file.name.lower()
    
    try:
        if filename.endswith(".csv") or filename.endswith(".txt"):
            st.session_state.df = pd.read_csv(uploaded_file)
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            st.session_state.df = pd.read_excel(uploaded_file)
        elif filename.endswith(".json"):
            st.session_state.df = pd.read_json(uploaded_file)
        else:
            st.error("Unsupported file format.")
            st.session_state.df = None
    except Exception as e:
        st.error(f"Error while reading file: {e}")
        st.session_state.df = None

def _render_preview_section():
    """Render data preview and editing section"""
    with st.expander("📋 Preview and Modify Data", expanded=True):
        st.subheader("Modify data before saving")
        st.session_state.df = st.data_editor(
            st.session_state.df, 
            width='stretch', 
            num_rows="dynamic"
        )

def _render_indices_section():
    """Render index configuration section"""
    with st.expander("🔍 Setup Indices"):
        indices = []
        
        selected_cols = st.multiselect(
            "Choose the columns to index", 
            options=list(st.session_state.df.columns)
        )
        
        for col in selected_cols:
            idx_type = st.selectbox(
                f"Index type for column '{col}'",
                options=["index", "columnar", "bitmap", "bitslice", "vector"],
                key=f"idx_{col}"
            )
            
            params = {}
            if idx_type == "vector":
                params["distance"] = st.selectbox(
                    f"Distance for column '{col}'", 
                    ["Cosine", "L2", "InnerProduct"], 
                    key=f"dist_{col}"
                )
                params["M"] = st.number_input(
                    f"M for {col}", 
                    min_value=4, 
                    max_value=64, 
                    value=16, 
                    step=1, 
                    key=f"M_{col}"
                )
                params["ef_construct"] = st.number_input(
                    f"ef_construct for {col}", 
                    min_value=50, 
                    max_value=1000, 
                    value=200, 
                    step=50, 
                    key=f"ef_{col}"
                )

            indices.append({"column": col, "type": idx_type, "params": params})
        
        # Store indices in session state for use in save section
        st.session_state.indices = indices

def _render_save_section(iris: IRIStool):
    """Render save configuration section"""
    st.subheader("💾 Save to IRIS Database")
    
    col1, col2, col3 = st.columns(3)

    with col1:
        table_name = st.text_input(
            "Table Name", 
            value="MyTable", 
            placeholder="Employees"
        )

    with col2:
        schema_name = st.text_input(
            "Table Schema", 
            value="SQLUser", 
            placeholder="SQLUser"
        )

    with col3:
        pk_col = st.selectbox(
            "Primary key (optional)", 
            options=["(none)"] + list(st.session_state.df.columns)
        )
        pk_col = None if pk_col == "(none)" else pk_col

    drop_existing = st.checkbox("Overwrite existing table", value=False)

    if st.button("💾 Save to Database", type="primary"):
        _save_to_database(
            iris, 
            table_name, 
            schema_name, 
            pk_col, 
            drop_existing
        )

def _save_to_database(
    iris: IRIStool, 
    table_name: str, 
    schema_name: str, 
    pk_col: Optional[str], 
    drop_existing: bool
):
    """Save DataFrame to IRIS database"""
    try:
        indices = st.session_state.get('indices', [])
        
        iris.df_to_table(
            st.session_state.df,
            table_name=table_name,
            table_schema=schema_name,
            primary_key=pk_col,
            exist_ok=drop_existing,
            drop_if_exists=drop_existing,
            indices=indices
        )
        
        st.success(f"✅ Successfully saved {len(st.session_state.df)} rows to {schema_name}.{table_name}")
        
    except Exception as e:
        st.error(f"❌ Error while saving: {e}")
        st.exception(e)