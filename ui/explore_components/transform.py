# ui/explore_components/transform.py
"""
Transform Component
Handles data transformation operations
"""

import streamlit as st
import pandas as pd
from utils.data_analysis import aggregate_data
import plotly.express as px

def render_transform(df: pd.DataFrame):
    """Render data transformation section"""
    
    if df is None or df.empty:
        st.warning("No data available for transformation")
        return
    
    transform_type = st.selectbox(
        "Select transformation",
        ["Group By & Aggregate"],
        help="Choose a transformation"
    )
    
    if transform_type == "Group By & Aggregate":
        _render_aggregate(df)

# ========== AGGREGATION ==========
def _render_aggregate(df: pd.DataFrame):
    """
     aggregation operation
    - Works on original df only
    - Results stored in separate session key
    - No dependencies on other operations
    """
    
    st.write("**Group By & Aggregate**")
    st.caption("Create aggregated view without modifying original data")
    
    if 'aggregation_result' not in st.session_state:
        st.session_state.aggregation_result = None
    
    group_cols = st.multiselect(
        "Group by columns", 
        df.columns.tolist(),
        key="agg_group_cols",
        help="Select columns to group by"
    )
    
    if group_cols:
        col1, col2 = st.columns(2)
        
        with col1:
            agg_col = st.selectbox(
                "Column to aggregate", 
                df.columns.tolist(),
                key="agg_target_col",
                help="Select column to calculate aggregate on"
            )
        
        with col2:
            agg_func = st.selectbox(
                "Aggregation function", 
                ["count", "sum", "mean", "min", "max", "std", "median"],
                key="agg_function"
            )
        
        col_btn1, col_btn2 = st.columns([1, 1])
        
        with col_btn1:
            if st.button("Calculate Aggregation", type="primary", width='stretch'):
                try:
                    st.session_state["show_agg_viz"] = False
                    aggregated_df = aggregate_data(df.copy(), group_cols, agg_col, agg_func)
                    st.session_state.aggregation_result = {
                        'data': aggregated_df,
                        'group_cols': group_cols,
                        'agg_col': agg_col,
                        'agg_func': agg_func
                    }
                    
                    st.success(f"Aggregation calculated! Grouped by {', '.join(group_cols)}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col_btn2:
            if st.session_state.aggregation_result is not None:
                if st.button("Clear Results", width='stretch'):
                    st.session_state.aggregation_result = None
                    st.success("Aggregation cleared")
                    st.rerun()
    
    if st.session_state.aggregation_result is not None:
        st.divider()
        st.subheader("Aggregation Results")
        
        agg_info = st.session_state.aggregation_result
        
        st.info(f"""
        **Details:**
        - Grouped by: {', '.join(agg_info['group_cols'])}
        - Aggregated column: {agg_info['agg_col']}
        - Function: {agg_info['agg_func']}
        - Result rows: {len(agg_info['data'])}
        """)
        
        st.dataframe(agg_info['data'], width='stretch', height=400)
        
        #  download
        csv = agg_info['data'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results (CSV)",
            data=csv,
            file_name=f"aggregation_{agg_info['agg_func']}.csv",
            mime="text/csv",
            width='stretch'
        )
        
        # Checkbox instead of button - stays active
        show_viz = st.checkbox("Show Visualization", key="show_agg_viz")
        
        if show_viz:
            chart_type = st.selectbox(
                "Chart type",
                ["Bar Chart", "Line Chart", "Pie Chart","Box Plot"],
                key="agg_chart_type"
            )
            # Now visualization updates automatically when chart_type changes
            _visualize_aggregation(agg_info['data'], agg_info['group_cols'], chart_type)

def _visualize_aggregation(agg_df: pd.DataFrame, group_cols: list, chart_type: str):
    """Visualization for aggregated data."""
    try:
        x_col = group_cols[0]
        y_col = agg_df.columns[-1]

        if len(group_cols) == 1:
            # One grouping column
            if chart_type == "Bar Chart":
                fig = px.bar(agg_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
            elif chart_type == "Line Chart":
                fig = px.line(agg_df, x=x_col, y=y_col, title=f"{y_col} by {x_col}", markers=True)
            elif chart_type == "Pie Chart":
                fig = px.pie(agg_df, names=x_col, values=y_col, title=f"{y_col} distribution")
            elif chart_type == "Box Plot":
                fig = px.box(agg_df, x=x_col, y=y_col, title=f"{y_col} distribution by {x_col}")
            else:
                st.warning("Unsupported chart type for single grouping.")
                return

        else:
            # Two or more grouping columns
            color_col = group_cols[1]

            if chart_type == "Bar Chart":
                fig = px.bar(agg_df, x=x_col, y=y_col, color=color_col, barmode='group',
                             title=f"{y_col} by {x_col} and {color_col}")
            elif chart_type == "Line Chart":
                fig = px.line(agg_df, x=x_col, y=y_col, color=color_col, markers=True,
                              title=f"{y_col} by {x_col} and {color_col}")
            elif chart_type == "Pie Chart":
                # Aggregate by color_col for pie
                pie_df = agg_df.groupby(color_col)[y_col].sum().reset_index()
                fig = px.pie(pie_df, names=color_col, values=y_col,
                             title=f"{y_col} distribution by {color_col}")
            elif chart_type == "Box Plot":
                fig = px.box(agg_df, x=x_col, y=y_col, color=color_col,
                             title=f"{y_col} distribution by {x_col} and {color_col}")
            else:
                st.warning("Unsupported chart type for multiple groupings.")
                return

        st.plotly_chart(fig, use_container_width=True, config={})

    except Exception as e:
        st.error(f"Visualization error: {e}")
