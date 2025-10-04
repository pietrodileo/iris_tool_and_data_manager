# ui/create_table_tab.py
"""
Create Table Tab UI Component
Allows manual table creation with custom schema
"""

import streamlit as st
from utils.iristool import IRIStool

def render_create_table_tab(iris: IRIStool):
    """Render the create table manually tab"""
    
    st.subheader("🛠️ Create Empty Table")
    st.write("Define a custom table structure and create it in IRIS database.")
    
    manual_cols = st.text_area(
        "Define the columns",
        placeholder="Name VARCHAR(100), Age INT, Salary DOUBLE",
        help="Format: ColumnName DataType, separated by commas. Example: Name VARCHAR(100), Age INT, Salary DOUBLE"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        manual_table = st.text_input(
            "Table name", 
            placeholder="MyManualTable",
            help="Name for the new table"
        )
    
    with col2:
        manual_schema = st.text_input(
            "Table schema", 
            placeholder="SQLUser",
            value="SQLUser",
            help="Database schema where the table will be created"
        )
    
    if st.button("✨ Create Empty Table", type="primary"):
        _create_table(iris, manual_table, manual_schema, manual_cols)

def _create_table(iris: IRIStool, table_name: str, schema_name: str, columns_str: str):
    """Create empty table in IRIS database"""
    
    # Validation
    if not table_name or not schema_name or not columns_str:
        st.error("❌ Please fill in all fields")
        return
    
    try:
        # Parse columns string into dictionary
        columns = _parse_columns(columns_str)
        
        if not columns:
            st.error("❌ Invalid column definition. Please check the format.")
            return
        
        # Create table
        iris.create_table(
            table_name=table_name,
            table_schema=schema_name,
            columns=columns
        )
        
        st.success(f"✅ Table {schema_name}.{table_name} has been successfully created with {len(columns)} columns.")
        
        # Show created columns
        with st.expander("📋 Created Table Structure"):
            for col_name, col_type in columns.items():
                st.write(f"- **{col_name}**: `{col_type}`")
        
    except Exception as e:
        st.error(f"❌ Error while creating table: {e}")
        st.exception(e)

def _parse_columns(columns_str: str) -> dict:
    """
    Parse column definition string into dictionary
    
    Args:
        columns_str: String like "Name VARCHAR(100), Age INT, Salary DOUBLE"
        
    Returns:
        Dictionary like {"Name": "VARCHAR(100)", "Age": "INT", "Salary": "DOUBLE"}
    """
    columns = {}
    
    try:
        for col_def in columns_str.split(","):
            col_def = col_def.strip()
            if not col_def:
                continue
            
            parts = col_def.split(None, 1)  # Split on first whitespace
            if len(parts) == 2:
                col_name = parts[0].strip()
                col_type = parts[1].strip()
                columns[col_name] = col_type
        
        return columns
    
    except Exception:
        return {}