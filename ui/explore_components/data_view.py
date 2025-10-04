# ui/explore_components/data_view.py
"""
Data View Component
Display table data and provide download options
"""

import streamlit as st
import pandas as pd
import io

def render_data_view(df: pd.DataFrame):
    """Render data view with download options"""
    
    st.subheader("📋 Table Data")
    
    # Display data
    st.dataframe(df, width='stretch', height=400)
    
    # Download buttons
    st.divider()
    _render_download_buttons(df)

def _render_download_buttons(df: pd.DataFrame):
    """Render download buttons for CSV and Excel"""
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    filename = f"{st.session_state.schema_input}.{st.session_state.selected_table}_export"
    
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"{filename}.csv",
            mime="text/csv",
            width='stretch'
        )
    
    with col2:
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)
        st.download_button(
            label="📥 Download Excel",
            data=excel_buffer,
            file_name=f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )
        
    with col3:
        # write table as json
        st.download_button(
            label="📥 Download JSON",
            data=df.to_json(orient='records'),
            file_name=f"{filename}.json",
            mime="application/json",
            width='stretch'
        )
        