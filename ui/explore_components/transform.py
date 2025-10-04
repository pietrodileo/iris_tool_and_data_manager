# ui/explore_components/transform.py
"""
Transform Component
Data transformation operations
"""

import streamlit as st
import pandas as pd
from utils.data_analysis import (
    aggregate_data, 
    create_calculated_column, 
    get_numeric_columns
)

def render_transform(df: pd.DataFrame):
    """Render data transformation section"""
    
    st.subheader("🔧 Data Transformation")
    
    # Get working dataframe (filtered or original)
    working_df = st.session_state.get('transformed_data', df)
    
    transform_type = st.selectbox(
        "Select transformation",
        ["Group By & Aggregate", "Create Calculated Column", "Sort Data"],
        help="Choose a transformation to apply to your data"
    )
    
    if transform_type == "Group By & Aggregate":
        _render_aggregate_transform(working_df)
    elif transform_type == "Create Calculated Column":
        _render_calculated_column_transform(working_df)
    elif transform_type == "Sort Data":
        _render_sort_transform(working_df)
    
    # Reset button
    st.divider()
    if st.button("🔄 Reset to Original Data", help="Clear all transformations and filters"):
        st.session_state.transformed_data = None
        st.success("✅ Data reset to original!")
        st.rerun()

def _render_aggregate_transform(df: pd.DataFrame):
    """Render group by & aggregate transformation"""    
    if df is None:
        st.error("⚠️ Nessun dataframe disponibile (df è None in render_transform)")
        return

    st.write("**Group By & Aggregate**")
    st.caption("Group data by one or more columns and calculate aggregates")
    
    group_cols = st.multiselect(
        "Group by columns", 
        df.columns.tolist(),
        help="Select columns to group by"
    )
    
    if group_cols:
        col1, col2 = st.columns(2)
        
        with col1:
            agg_col = st.selectbox(
                "Column to aggregate", 
                df.columns.tolist(),
                help="Select column to calculate aggregate on"
            )
        
        with col2:
            agg_func = st.selectbox(
                "Aggregation function", 
                ["sum", "mean", "count", "min", "max", "std"],
                help="Select how to aggregate the data"
            )
        
        if st.button("📊 Apply Aggregation", type="primary"):
            try:
                grouped = aggregate_data(df, group_cols, agg_col, agg_func)
                st.session_state.transformed_data = grouped
                st.success(f"✅ Aggregation applied! Grouped by {', '.join(group_cols)}")
                st.dataframe(grouped, width='stretch')
            except Exception as e:
                st.error(f"❌ Error: {e}")

def _render_calculated_column_transform(df: pd.DataFrame):
    """Render create calculated column transformation"""
    
    st.write("**Create Calculated Column**")
    st.caption("Create a new column based on mathematical operations between two columns")
    
    new_col_name = st.text_input(
        "New column name", 
        "calculated_column",
        help="Name for the new calculated column"
    )
    
    numeric_cols = get_numeric_columns(df)
    
    if len(numeric_cols) >= 2:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            col_a = st.selectbox(
                "First column", 
                numeric_cols, 
                key="calc_col1"
            )
        
        with col2:
            operation = st.selectbox(
                "Operation", 
                ["+", "-", "*", "/"],
                format_func=lambda x: {
                    "+": "➕ Add",
                    "-": "➖ Subtract",
                    "*": "✖️ Multiply",
                    "/": "➗ Divide"
                }[x]
            )
        
        with col3:
            col_b = st.selectbox(
                "Second column", 
                numeric_cols, 
                key="calc_col2"
            )
        
        st.caption(f"Formula: `{new_col_name} = {col_a} {operation} {col_b}`")
        
        if st.button("➕ Create Column", type="primary"):
            try:
                new_df = create_calculated_column(df, new_col_name, col_a, operation, col_b)
                st.session_state.transformed_data = new_df
                st.success(f"✅ Column '{new_col_name}' created!")
                st.dataframe(new_df[[col_a, col_b, new_col_name]].head(10), width='stretch')
            except Exception as e:
                st.error(f"❌ Error: {e}")
    else:
        st.warning("⚠️ Need at least 2 numeric columns for calculations")

def _render_sort_transform(df: pd.DataFrame):
    """Render sort data transformation"""
    if df is None:
        st.error("⚠️ Nessun dataframe disponibile (df è None in render_transform)")
        return

    st.write("**Sort Data**")
    st.caption("Sort the data by one or more columns")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sort_cols = st.multiselect(
            "Sort by columns", 
            df.columns.tolist(),
            help="Select one or more columns to sort by"
        )
    
    with col2:
        ascending = st.checkbox(
            "Ascending order", 
            value=True,
            help="Check for ascending, uncheck for descending"
        )
    
    if sort_cols and st.button("🔽 Apply Sort", type="primary"):
        try:
            sorted_df = df.sort_values(by=sort_cols, ascending=ascending)
            st.session_state.transformed_data = sorted_df
            st.success(f"✅ Data sorted by {', '.join(sort_cols)} ({'ascending' if ascending else 'descending'})")
            st.dataframe(sorted_df.head(10), width='stretch')
        except Exception as e:
            st.error(f"❌ Error: {e}")