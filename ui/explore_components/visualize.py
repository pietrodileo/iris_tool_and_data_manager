# ui/explore_components/visualize.py
"""
Visualize Component
Interactive data visualization with integrated filtering
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_analysis import (
    get_numeric_columns,
    get_categorical_columns,
    apply_filters
)

def render_visualize(df: pd.DataFrame):
    """Render interactive visualization section with integrated filters"""
    
    st.subheader("📈 Interactive Visualization")
    
    # Integrated filtering at the top
    with st.expander("🎯 Filter Data Before Visualizing", expanded=False):
        _render_integrated_filters(df)
    
        # Get the data to visualize (filtered or original)
        viz_data = st.session_state.get('transformed_data', df)
        
        if viz_data is None or viz_data.empty:
            st.warning("⚠️ No data available for visualization")
            return
        
        # Show current data status
        _render_data_status(df, viz_data)
        
        # Show current data in a table for reference
        _render_data_table(viz_data)
    
    st.divider()
    
    # Chart configuration and rendering
    _render_chart_section(viz_data)

def _render_integrated_filters(df: pd.DataFrame):
    """Render integrated filtering section"""
    
    st.markdown("#### Apply Filters")
    st.caption("Filter your data before creating visualizations. Filters apply to all charts below.")
    
    # Current filter status
    transformed_data = st.session_state.get('transformed_data')

    if transformed_data is not None and len(transformed_data) != len(df):
        filtered_count = len(transformed_data)
        total_count = len(df)
        filtered_pct = (filtered_count / total_count * 100) if total_count > 0 else 0
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info(f"🔍 **Active Filters**: Showing {filtered_count:,} of {total_count:,} rows ({filtered_pct:.1f}%)")
        with col2:
            if st.button("🗑️ Clear Filters", use_container_width=True, key="clear_filters_viz"):
                _reset_all_filters(df)
                st.session_state.transformed_data = None
                st.rerun()
    
    # Filter controls
    active_filters = {}
    
    # Numeric filters
    numeric_cols = get_numeric_columns(df)
    if numeric_cols:
        with st.expander("🔢 Numeric Filters", expanded=False): 
            active_filters.update(_render_numeric_filters_compact(df, numeric_cols))
    
    # Categorical filters
    categorical_cols = get_categorical_columns(df)
    if categorical_cols:
        with st.expander("📑 Categorical Filters", expanded=False):
           active_filters.update(_render_categorical_filters_compact(df, categorical_cols))
    
    # Apply filters
    if active_filters:
        filtered_df = apply_filters(df, active_filters)
        st.session_state.transformed_data = filtered_df
        
        # Show active filters summary
        st.markdown("**Active Filters:**")
        for col, filter_config in active_filters.items():
            if filter_config['type'] == 'numeric':
                min_val, max_val = filter_config['range']
                st.caption(f"• **{col}**: {min_val:.2f} to {max_val:.2f}")
            elif filter_config['type'] == 'categorical':
                selected_count = len(filter_config['selected'])
                st.caption(f"• **{col}**: {selected_count} values selected")
    else:
        st.session_state.transformed_data = df

def _reset_all_filters(df: pd.DataFrame):
    """Reset all filters to their default values"""
    # Reset numeric filters
    for col in get_numeric_columns(df):
        col_data = df[col].dropna()
        
        # Only reset if there's valid data
        if len(col_data) > 0:
            min_val = float(col_data.min())
            max_val = float(col_data.max())
            
            # Only set if valid range
            if not pd.isna(min_val) and not pd.isna(max_val) and min_val != max_val:
                st.session_state[f"viz_filter_num_{col}"] = (min_val, max_val)
    
    # Reset categorical filters
    categorical_cols = get_categorical_columns(df)
    for col in categorical_cols:
        if df[col].dropna().nunique() <= 50:
            unique_vals = df[col].dropna().unique().tolist()
            if unique_vals:  # Only reset if there are values
                st.session_state[f"viz_filter_cat_{col}"] = unique_vals

def _render_numeric_filters_compact(df: pd.DataFrame, numeric_cols: list) -> dict:
    """Render compact numeric filters in grid"""
    
    filters = {}
    cols_per_row = 4
    num_rows = (len(numeric_cols) + cols_per_row - 1) // cols_per_row
    
    for row_idx in range(num_rows):
        cols = st.columns(cols_per_row)
        
        for col_idx in range(cols_per_row):
            idx = row_idx * cols_per_row + col_idx
            if idx >= len(numeric_cols):
                break
            
            col = numeric_cols[idx]
            
            with cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"**{col}**")
                    
                    # Handle NaN values - use dropna() for min/max calculation
                    col_data = df[col].dropna()
                    
                    if len(col_data) == 0:
                        # All values are NaN
                        st.caption("⚠️ All values are NaN")
                        st.caption("Cannot create filter")
                        continue
                    
                    min_val = float(col_data.min())
                    max_val = float(col_data.max())
                    
                    # Check if min and max are valid
                    if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
                        st.caption(f"Value: {min_val:.2f}")
                        st.caption("⚠️ Single value or invalid range")
                        continue
                    
                    st.caption(f"{min_val:.2f} - {max_val:.2f}")
                    
                    selected_range = st.slider(
                        f"Range",
                        min_val,
                        max_val,
                        (min_val, max_val),
                        key=f"viz_filter_num_{col}",
                        label_visibility="collapsed"
                    )
                    
                    if selected_range != (min_val, max_val):
                        filters[col] = {'type': 'numeric', 'range': selected_range}
    
    return filters

def _render_categorical_filters_compact(df: pd.DataFrame, categorical_cols: list) -> dict:
    """Render compact categorical filters in grid"""
    
    filters = {}
    cols_per_row = 4
    
    filterable_cols = [
        col for col in categorical_cols 
        if df[col].dropna().nunique() <= 50
    ]
    
    if not filterable_cols:
        st.caption("⚠️ No categorical columns with <50 unique values")
        return filters
    
    num_rows = (len(filterable_cols) + cols_per_row - 1) // cols_per_row
    
    for row_idx in range(num_rows):
        cols = st.columns(cols_per_row)
        
        for col_idx in range(cols_per_row):
            idx = row_idx * cols_per_row + col_idx
            if idx >= len(filterable_cols):
                break
            
            col = filterable_cols[idx]
            unique_vals = df[col].dropna().unique().tolist()
            
            with cols[col_idx]:
                with st.container(border=True):
                    st.markdown(f"**{col}**")
                    st.caption(f"{len(unique_vals)} values")
                    
                    selected_vals = st.multiselect(
                        f"Select",
                        options=unique_vals,
                        default=unique_vals,
                        key=f"viz_filter_cat_{col}",
                        label_visibility="collapsed"
                    )
                    
                    if len(selected_vals) < len(unique_vals):
                        filters[col] = {'type': 'categorical', 'selected': selected_vals}
    
    return filters

def _render_data_status(original_df: pd.DataFrame, viz_data: pd.DataFrame):
    """Render current data status for visualization"""
    
    if len(viz_data) == len(original_df):
        st.success(f"✅ Visualizing all {len(viz_data):,} rows")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Visualizing", f"{len(viz_data):,} rows")
        col2.metric("Filtered Out", f"{len(original_df) - len(viz_data):,} rows")
        col3.metric("Percentage", f"{(len(viz_data)/len(original_df)*100):.1f}%")

def _render_chart_section(viz_data: pd.DataFrame):
    """Render chart configuration and display"""
    
    st.markdown("### 📊 Chart Configuration")
    
    numeric_cols = get_numeric_columns(viz_data)
    all_cols = viz_data.columns.tolist()
    
    # Chart type and color selection
    col1, col2 = st.columns(2)
    
    with col1:
        chart_type = st.selectbox(
            "Chart Type",
            [
                "Scatter", "Line", "Bar", "Histogram", 
                "Box Plot", "Pie Chart", "Heatmap"
            ],
            key="chart_type_viz",
            help="Select the type of chart to display"
        )
    
    with col2:
        color_by = st.selectbox(
            "Color by (optional)", 
            ["None"] + all_cols, 
            key="color_by_viz",
            help="Color data points by a specific column"
        )
        color_by = None if color_by == "None" else color_by
    
    # Create and display chart
    fig = _create_chart(viz_data, chart_type, numeric_cols, all_cols, color_by)
    
    if fig:
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)

def _create_chart(df, chart_type, numeric_cols, all_cols, color_by):
    """Create chart based on selected type"""
    
    if chart_type in ["Scatter", "Line"]:
        return _create_xy_chart(df, chart_type, numeric_cols, all_cols, color_by)
    elif chart_type == "Bar":
        return _create_bar_chart(df, numeric_cols, all_cols, color_by)
    elif chart_type == "Histogram":
        return _create_histogram(df, numeric_cols, all_cols, color_by)
    elif chart_type == "Box Plot":
        return _create_box_plot(df, numeric_cols, all_cols, color_by)
    elif chart_type == "Pie Chart":
        return _create_pie_chart(df, numeric_cols, all_cols)
    elif chart_type == "Heatmap":
        return _create_heatmap(df, numeric_cols)
    
    return None

def _create_xy_chart(df, chart_type, numeric_cols, all_cols, color_by):
    """Create scatter or line chart"""
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        x_axis = st.selectbox("X axis", options=all_cols, key="x_axis_viz")
    with col_b:
        y_axis = st.selectbox("Y axis", options=all_cols, key="y_axis_viz")
    
    if chart_type == "Scatter":
        size_by = st.selectbox(
            "Size by (optional)", 
            ["None"] + numeric_cols, 
            key="size_by_viz"
        )
        size_by = None if size_by == "None" else size_by
        
        return px.scatter(
            df, x=x_axis, y=y_axis, 
            color=color_by, size=size_by,
            hover_data=all_cols, 
            title=f"Scatter: {y_axis} vs {x_axis}"
        )
    else:
        return px.line(
            df, x=x_axis, y=y_axis, 
            color=color_by,
            hover_data=all_cols, 
            title=f"Line: {y_axis} vs {x_axis}"
        )

def _create_bar_chart(df, numeric_cols, all_cols, color_by):
    """Create bar chart"""
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        x_axis = st.selectbox("X axis (categories)", options=all_cols, key="x_axis_bar_viz")
    with col_b:
        y_axis = st.selectbox(
            "Y axis (values)", 
            options=numeric_cols if numeric_cols else all_cols, 
            key="y_axis_bar_viz"
        )
    
    return px.bar(
        df, x=x_axis, y=y_axis, 
        color=color_by, 
        title=f"Bar Chart: {y_axis} by {x_axis}"
    )

def _create_histogram(df, numeric_cols, all_cols, color_by):
    """Create histogram"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        x_axis = st.selectbox(
            "Column to analyze", 
            options=numeric_cols if numeric_cols else all_cols, 
            key="x_axis_hist_viz"
        )
    with col2:
        nbins = st.slider(
            "Number of bins", 
            min_value=5, 
            max_value=100, 
            value=20, 
            key="hist_bins_viz"
        )
    
    return px.histogram(
        df, x=x_axis, 
        color=color_by, 
        nbins=nbins, 
        title=f"Histogram: {x_axis}"
    )

def _create_box_plot(df, numeric_cols, all_cols, color_by):
    """Create box plot"""
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        y_axis = st.selectbox(
            "Y axis (values)", 
            options=numeric_cols if numeric_cols else all_cols, 
            key="y_axis_box_viz"
        )
    with col_b:
        x_axis = st.selectbox(
            "X axis (categories, optional)", 
            options=["None"] + all_cols, 
            key="x_axis_box_viz"
        )
        x_axis = None if x_axis == "None" else x_axis
    
    return px.box(
        df, x=x_axis, y=y_axis, 
        color=color_by, 
        title=f"Box Plot: {y_axis}"
    )

def _create_pie_chart(df, numeric_cols, all_cols):
    """Create pie chart"""
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        names_col = st.selectbox("Labels", options=all_cols, key="pie_names_viz")
    with col_b:
        values_col = st.selectbox(
            "Values", 
            options=numeric_cols if numeric_cols else all_cols, 
            key="pie_values_viz"
        )
    
    return px.pie(
        df, 
        names=names_col, 
        values=values_col, 
        title=f"Pie Chart: {values_col} by {names_col}"
    )

def _create_heatmap(df, numeric_cols):
    """Create correlation heatmap"""
    
    if len(numeric_cols) > 1:
        corr_matrix = df[numeric_cols].corr()
        return px.imshow(
            corr_matrix, 
            text_auto=True, 
            aspect="auto",
            title="Correlation Heatmap", 
            labels=dict(color="Correlation")
        )
    else:
        st.warning("⚠️ Heatmap requires at least 2 numeric columns")
        return None
    
def _render_data_table(df: pd.DataFrame):
    """Render data table"""
    st.dataframe(df, width='stretch', height=400)