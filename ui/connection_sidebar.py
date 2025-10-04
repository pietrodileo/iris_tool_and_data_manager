# ui/connection_sidebar.py
"""
Connection Sidebar Component
Manage IRIS database connection with custom or default settings in sidebar
"""

import streamlit as st
from utils.iristool import IRIStool
from config.settings import AppConfig
import logging

logger = logging.getLogger(__name__)

# ---------- Initialize Connection ----------
@st.cache_resource
def init_connection(IRIS_HOST: str, IRIS_PORT: str, IRIS_NAMESPACE: str, IRIS_USER: str, IRIS_PASSWORD: str):
    """Initialize and cache IRIS database connection"""
    return IRIStool(
        host=IRIS_HOST,
        port=IRIS_PORT,
        namespace=IRIS_NAMESPACE,
        username=IRIS_USER,
        password=IRIS_PASSWORD
    )

def render_connection_sidebar(config: AppConfig):
    """Render connection management in sidebar"""
    
    with st.sidebar:
        st.markdown("## 🔌 Database Connection")
        
        # Display connection status
        _render_connection_status()
        
        st.divider()
        
        # Connection form
        _render_connection_form(config)

def _render_connection_status():
    """Render connection status banner"""
    
    if st.session_state.iris_connection is not None:
        st.success("✅ **Connected**")
        
        # Show connection details
        with st.expander("📋 Connection Info", expanded=False):
            conn = st.session_state.iris_connection
            st.caption(f"**Host:** {conn.host}")
            st.caption(f"**Port:** {conn.port}")
            st.caption(f"**Namespace:** {conn.namespace}")
            st.caption(f"**User:** {conn.username}")
            
            # Test connection button
            if st.button("🔍 Test Connection", width='stretch', key="test_conn"):
                _test_connection()
            
            # Disconnect button
            if st.button("🔴 Disconnect", width='stretch', type="secondary", key="disconnect"):
                _disconnect()
    else:
        st.error("❌ **Not Connected**")
        st.caption("Enter credentials below to connect")

def _render_connection_form(config):
    """Render connection configuration form"""
    
    try:
        st.markdown("### ⚙️ Connection Settings")
        
        # Connection parameters
        host = st.text_input(
            "Host",
            value=config.IRIS_HOST if config.IRIS_HOST else "localhost",
            placeholder="localhost",
            key="conn_host",
            help="IRIS server hostname or IP"
        )
        
        port = st.text_input(
            "Port",
            value=config.IRIS_PORT if config.IRIS_PORT else "1972",
            placeholder="1972",
            key="conn_port",
            help="IRIS server port"
        )
        
        namespace = st.text_input(
            "Namespace",
            value=config.IRIS_NAMESPACE if config.IRIS_NAMESPACE else "USER",
            placeholder="USER",
            key="conn_namespace",
            help="IRIS namespace"
        )
        
        user = st.text_input(
            "Username",
            value=config.IRIS_USER if config.IRIS_USER else "_SYSTEM",
            placeholder="_SYSTEM",
            key="conn_user",
            help="Database username"
        )
        
        password = st.text_input(
            "Password",
            value=config.IRIS_PASSWORD if config.IRIS_PASSWORD else "",
            placeholder="Password",
            type="password",
            key="conn_password",
            help="Database password"
        )
        
        # Validation
        all_fields_filled = all([host, port, namespace, user, password])
        
        # Connect/Reconnect button
        button_label = "🔄 Reconnect" if st.session_state.iris_connection is not None else "🔌 Connect"
        button_type = "secondary" if st.session_state.iris_connection is not None else "primary"
        
        if st.button(
            button_label,
            width='stretch',
            type=button_type,
            disabled=not all_fields_filled,
            key="connect_btn"
        ):
            _connect(host, port, namespace, user, password)
        
        if not all_fields_filled:
            st.caption("⚠️ Please fill in all fields")
        
        # Load from .env hint
        if config.IRIS_HOST:
            st.caption("💡 Default values loaded from `.env` file")
    
    except Exception as e:
        st.error(f"❌ Configuration error: {e}")
        st.caption("Make sure your `.env` file is properly configured")

def _connect(host: str, port: str, namespace: str, user: str, password: str):
    """Establish database connection"""
    
    with st.spinner("🔄 Connecting to IRIS database..."):
        try:
            # Clear existing connection from cache if reconnecting
            if st.session_state.iris_connection is not None:
                init_connection.clear()
            
            st.session_state.iris_connection = init_connection(
                IRIS_HOST=host,
                IRIS_PORT=port,
                IRIS_NAMESPACE=namespace,
                IRIS_USER=user,
                IRIS_PASSWORD=password
            )
            st.session_state.connection_status = "Connected"
            st.session_state.use_default_connection = True
            
            logger.info(f"Successfully connected to {host}:{port}/{namespace}")
            st.success("✅ Connected successfully!")
            st.rerun()
            
        except Exception as e:
            st.session_state.connection_status = f"Failed: {str(e)}"
            st.session_state.iris_connection = None
            logger.error(f"Connection failed: {e}")
            st.error(f"❌ Connection failed: {e}")

def _disconnect():
    """Disconnect from database"""
    
    try:
        # Clear cached connection
        init_connection.clear()
        
        # Clear session state
        st.session_state.iris_connection = None
        st.session_state.connection_status = "Disconnected"
        st.session_state.table_data = None
        st.session_state.transformed_data = None
        st.session_state.filters = {}
        
        logger.info("Disconnected from IRIS database")
        st.success("✅ Disconnected successfully")
        st.rerun()
        
    except Exception as e:
        logger.error(f"Disconnect error: {e}")
        st.error(f"❌ Error during disconnect: {e}")

def _test_connection():
    """Test the current database connection"""
    
    try:
        if st.session_state.iris_connection:
            # Try a simple query to test connection
            result = st.session_state.iris_connection.fetch("SELECT 1 as Test")
            
            if not result.empty:
                st.success("✅ Connection is active and working!")
            else:
                st.warning("⚠️ Connection established but test query returned empty result")
        else:
            st.error("❌ No active connection")
            
    except Exception as e:
        st.error(f"❌ Connection test failed: {e}")
        logger.error(f"Connection test failed: {e}")