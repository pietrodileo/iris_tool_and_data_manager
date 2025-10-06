# ui/explore_components/data_profile.py
"""
Data Profile Component
Display comprehensive data quality and statistics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import json
from utils.data_analysis import generate_data_profile
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID

def convert_keys_to_str(obj):
    """Recursively convert dict keys to strings and values to JSON-safe."""
    if isinstance(obj, dict):
        return {str(k): convert_keys_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_keys_to_str(v) for v in obj]
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, UUID):
        return str(obj)
    else:
        return obj

def render_data_profile(df: pd.DataFrame):
    """Render data profiling section"""
    
    st.subheader("📊 Data Quality & Statistics")
    
    profile = generate_data_profile(df)
    
    # Overview metrics and download button
    col1, col2 = st.columns([4, 1])
    
    with col1:
        _render_overview_metrics(profile['overview'])
    
    with col2:
        st.write("")  # Spacing
        _render_download_button(profile)
    
    st.divider()
    
    # Column-by-column analysis with grid layout
    st.markdown("### 📋 Column Analysis")
    
    # Separate numeric and categorical columns
    numeric_cols = {k: v for k, v in profile['columns'].items() if 'mean' in v}
    categorical_cols = {k: v for k, v in profile['columns'].items() if 'mean' not in v}
    
    if numeric_cols:
        st.markdown("#### 🔢 Numeric Columns")
        _render_numeric_columns_grid(df, numeric_cols)
    
    if categorical_cols:
        st.markdown("#### 📑 Categorical Columns")
        _render_categorical_columns_grid(df, categorical_cols)

def _render_overview_metrics(overview: dict):
    """Render overview metrics cards"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("📊 Total Rows", f"{overview['rows']:,}")
    col2.metric("📋 Total Columns", overview['columns'])
    col3.metric("💾 Memory Usage", overview['memory_usage'])
    col4.metric("🔄 Duplicates", overview['duplicates'])

def _render_download_button(profile: dict):
    """Render download button for profile stats as JSON"""
    
    # Convert profile to JSON-serializable format
    profile_json = _prepare_profile_for_json(profile)
    
    # Create JSON string
    serializable_profile = convert_keys_to_str(profile_json)
    json_str = json.dumps(serializable_profile, indent=2)
    
    filename = f"{st.session_state.schema_input}.{st.session_state.selected_table}_data_profile_stats.json"

    # Download button
    st.download_button(
        label="📥 Download Stats",
        data=json_str,
        file_name=filename,
        mime="application/json",
        width='stretch',
        help="Download all statistics as JSON file"
    )

def _prepare_profile_for_json(profile: dict) -> dict:
    """Prepare profile dictionary for JSON serialization"""
    
    def convert_value(val):
        """Convert numpy/pandas types to Python native types"""
        if pd.isna(val):
            return None
        if isinstance(val, (pd.Timestamp, pd.Timedelta)):
            return str(val)
        if hasattr(val, 'item'):  # numpy types
            return val.item()
        return val
    
    def convert_dict(d):
        """Recursively convert dictionary values"""
        if isinstance(d, dict):
            return {k: convert_dict(v) for k, v in d.items()}
        elif isinstance(d, (list, tuple)):
            return [convert_dict(item) for item in d]
        else:
            return convert_value(d)
    
    return convert_dict(profile)

def _render_numeric_columns_grid(df: pd.DataFrame, numeric_cols: dict):
    """Render numeric columns in a grid layout (4 per row)"""
    
    cols_per_row = 4
    col_names = list(numeric_cols.keys())
    num_rows = (len(col_names) + cols_per_row - 1) // cols_per_row
    
    for row_idx in range(num_rows):
        cols = st.columns(cols_per_row)
        
        for col_idx in range(cols_per_row):
            idx = row_idx * cols_per_row + col_idx
            
            if idx >= len(col_names):
                break
            
            col_name = col_names[idx]
            col_stats = numeric_cols[col_name]
            
            with cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"**{col_name}**")
                    st.caption(f"Type: `{col_stats['dtype']}`")
                    
                    # Key metrics in compact format
                    metric_col1, metric_col2 = st.columns(2)
                    with metric_col1:
                        st.metric("Mean", col_stats['mean'], label_visibility="visible")
                        st.metric("Min", col_stats['min'], label_visibility="visible")
                    with metric_col2:
                        st.metric("Std Dev", col_stats['std'], label_visibility="visible")
                        st.metric("Max", col_stats['max'], label_visibility="visible")
                    
                    # Missing values
                    if col_stats['missing'] > 0:
                        st.warning(f"⚠️ Missing: {col_stats['missing']} ({col_stats['missing_pct']})")
                    else:
                        st.success(f"✓ No missing values")
                    
                    # Expandable distribution plot
                    with st.expander("📊 View Distribution"):
                        fig = px.histogram(
                            df, 
                            x=col_name, 
                            title=f"Distribution",
                            nbins=30
                        )
                        fig.update_layout(height=250, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True, config={})

def _render_categorical_columns_grid(df: pd.DataFrame, categorical_cols: dict):
    """Render categorical columns in a grid layout (4 per row)"""
    
    cols_per_row = 4
    col_names = list(categorical_cols.keys())
    num_rows = (len(col_names) + cols_per_row - 1) // cols_per_row
    
    for row_idx in range(num_rows):
        cols = st.columns(cols_per_row)
        
        for col_idx in range(cols_per_row):
            idx = row_idx * cols_per_row + col_idx
            
            if idx >= len(col_names):
                break
            
            col_name = col_names[idx]
            col_stats = categorical_cols[col_name]
            
            with cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"**{col_name}**")
                    st.caption(f"Type: `{col_stats['dtype']}`")
                    
                    # Key metrics
                    metric_col1, metric_col2 = st.columns(2)
                    with metric_col1:
                        st.metric("Unique", col_stats['unique'], label_visibility="visible")
                    with metric_col2:
                        st.metric("Unique %", col_stats['unique_pct'], label_visibility="visible")
                    
                    # Missing values
                    if col_stats['missing'] > 0:
                        st.warning(f"⚠️ Missing: {col_stats['missing']} ({col_stats['missing_pct']})")
                    else:
                        st.success(f"✓ No missing values")
                    
                    # Top values
                    if 'top_values' in col_stats and col_stats['top_values']:
                        with st.expander("📋 Top Values"):
                            for val, count in list(col_stats['top_values'].items())[:3]:
                                st.caption(f"• **{val}**: {count}")
                            
                            # Bar chart
                            fig = px.bar(
                                x=list(col_stats['top_values'].keys()), 
                                y=list(col_stats['top_values'].values()),
                                title="Value Distribution",
                                labels={'x': col_name, 'y': 'Count'}
                            )
                            fig.update_layout(height=250, showlegend=False)
                            st.plotly_chart(fig, use_container_width=True, config={})