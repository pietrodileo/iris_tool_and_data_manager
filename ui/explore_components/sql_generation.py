# ui/explore_components/sql_generation.py
"""
SQL Generation Component
Convert natural language to SQL using Ollama with Pydantic models
"""

import streamlit as st
from typing import Optional, List
import json
from utils.ollama_request import OllamaRequest
import logging

logger = logging.getLogger(__name__)

def render_sql_generation():
    """Render SQL generation section using Ollama"""
    
    llm = OllamaRequest(st.session_state["ollama_api_url"])
    
    st.markdown("### 💬 Ask Your Question")
    st.caption("Convert your questions into SQL queries using AI")

    # Model selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        user_question = st.text_area(
            "What do you want to know?",
            placeholder="e.g., Show me the top 10 customers by total sales\ne.g., What's the average order value by region?",
            height=100,
            help="Describe what you want to query in natural language"
        )
    
    with col2:
        st.write("") 
        available_models = ['gemma3:1b','gemma2:2b']
        selected_model = st.selectbox(
            "Model",
            options=available_models,
            help="Select the Ollama model to use"
        )
        
        generate_btn = st.button("🚀 Generate SQL", width='stretch', type="primary")
    
    # Generate SQL query
    if generate_btn and user_question:
        with st.spinner("🤖 Generating SQL query..."):
            sql_query,explanation = _generate_sql_query(llm, user_question, selected_model)

        if sql_query:
            _render_query_result(sql_query,explanation)
    
def _generate_sql_query(llm: OllamaRequest, question: str, model: str) -> tuple[Optional[str], Optional[str]]:
    """Generate SQL query using Ollama with structured output"""
    
    # Get info about the table
    table_info = st.session_state.iris_connection.describe_table(table_schema=st.session_state.schema_input, table_name=st.session_state.selected_table)
    # convert to json
    columns = table_info["columns"]
    table_info_str = json.dumps(columns)    
    indexes = table_info["indexes"]
    table_info_str += json.dumps(indexes)
    
    # Create the prompt
    prompt = f"""You are an expert SQL query generator. Given a natural language question and database schema, generate a SQL query.

Question: {question}

Generate a SQL query that answers this question. The query must:
1. Use only the columns that exist in the schema
2. Be syntactically correct
3. Be optimized and efficient
4. Handle NULL values appropriately

The SQL statement must be a select from the following table '{st.session_state.schema_input}.{st.session_state.selected_table}'.
The following are the info about the table:
{table_info_str}
"""

    try:
        # Call Ollama
        format = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string"
                },
                "explanation": {
                    "type": "string"
                }
            },
            "required": ["query", "explanation"]
        }
        
        response_json = llm.get_response(prompt, model, format)
        content_str = response_json['message']["content"]
        content = json.loads(content_str)
        sql_query = content["query"]
        explanation = content["explanation"]
        return sql_query, explanation
        
    except json.JSONDecodeError as e:
        st.error(f"❌ Failed to parse response: {e}")
        return None
    except Exception as e:
        st.error(f"❌ Error generating query: {e}")
        return None


def _render_query_result(query: str, explanation: str):
    """Render the generated query result"""
    
    st.success("✅ SQL Query Generated Successfully!")
    
    # Display the SQL query
    st.markdown("#### 📝 Generated SQL Query")
    st.code(query, language="sql")
    
    # Display the query explanation
    st.markdown("#### 📝 Query Explanation")
    st.write(explanation)
    
    # Display the query result
    st.markdown("#### 📊 Query Result")
            
    result = st.session_state.iris_connection.fetch(query)
    st.dataframe(result, width='stretch')