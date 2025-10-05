# ui/explore_components/sql_generation.py
"""
SQL Generation Component
Convert natural language to SQL using Ollama with Pydantic models
"""

import streamlit as st
from typing import Optional, List
import json
import re
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
        available_models = ['gemma3:1b','gemma2:2b','gemma3:4b']
        selected_model = st.selectbox(
            "Model",
            options=available_models,
            help="Select the Ollama model to use"
        )
        
        generate_btn = st.button("🚀 Generate SQL", use_container_width=True, type="primary")
    
    # Generate SQL query
    if generate_btn and user_question:
        with st.spinner("🤖 Generating SQL query..."):
            sql_query, explanation = _generate_sql_query(llm, user_question, selected_model)

        if sql_query:
            # Remove ';' if it exists
            sql_query = sql_query.replace(";", "")
            _render_query_result(sql_query, explanation)

def _validate_and_fix_sql(sql_query: str) -> tuple[str, List[str]]:
    """Validate and fix SQL query for IRIS compatibility"""
    
    issues = []
    fixed_query = sql_query
    
    # Check for LIMIT clause
    limit_match = re.search(r'\s+LIMIT\s+(\d+)', fixed_query, re.IGNORECASE)
    if limit_match:
        limit_value = limit_match.group(1)
        issues.append(f"Removed LIMIT {limit_value} (not supported in InterSystems IRIS)")
        
        # Try to convert to TOP if SELECT statement
        select_match = re.search(r'^\s*SELECT\s+', fixed_query, re.IGNORECASE)
        if select_match:
            # Check if TOP already exists
            if not re.search(r'SELECT\s+TOP\s+\d+', fixed_query, re.IGNORECASE):
                fixed_query = re.sub(
                    r'(^\s*SELECT\s+)', 
                    f'\\1TOP {limit_value} ', 
                    fixed_query, 
                    flags=re.IGNORECASE
                )
                issues.append(f"Converted to TOP {limit_value}")
        
        # Remove the LIMIT clause
        fixed_query = re.sub(r'\s+LIMIT\s+\d+\s*', ' ', fixed_query, flags=re.IGNORECASE)
    
    # Check for OFFSET clause
    if re.search(r'\s+OFFSET\s+\d+', fixed_query, re.IGNORECASE):
        issues.append("Removed OFFSET (not supported in InterSystems IRIS)")
        fixed_query = re.sub(r'\s+OFFSET\s+\d+\s*', ' ', fixed_query, flags=re.IGNORECASE)
    
    return fixed_query.strip(), issues
    
def _generate_sql_query(llm: OllamaRequest, question: str, model: str) -> tuple[Optional[str], Optional[str]]:
    """Generate SQL query using Ollama with structured output"""
    
    # Get info about the table
    table_info = st.session_state.iris_connection.describe_table(
        table_schema=st.session_state.schema_input, 
        table_name=st.session_state.selected_table
    )
    
    # Convert to json
    columns = table_info["columns"]
    table_info_str = json.dumps(columns)    
    indexes = table_info["indexes"]
    table_info_str += json.dumps(indexes)
    
    # Create the prompt with strong emphasis on IRIS SQL syntax
    prompt = f"""You are an expert SQL query generator for InterSystems IRIS database.

Question: {question}

Database Table: {st.session_state.schema_input}.{st.session_state.selected_table}
Schema Information:
{table_info_str}

CRITICAL REQUIREMENTS FOR INTERSYSTEMS IRIS SQL:
1. Use only columns that exist in the schema above
2. Be syntactically correct for InterSystems IRIS SQL
3. Be optimized and efficient
4. Handle NULL values appropriately
5. **NEVER use LIMIT or OFFSET keywords** - these are NOT supported in IRIS

SYNTAX RULES:
- ✅ CORRECT: SELECT TOP 10 * FROM table ORDER BY column
- ❌ WRONG:   SELECT * FROM table ORDER BY column LIMIT 10

- ✅ CORRECT: SELECT * FROM table WHERE condition
- ❌ WRONG:   SELECT * FROM table WHERE condition LIMIT 100

FORBIDDEN KEYWORDS IN IRIS:
- LIMIT (not supported)
- OFFSET (not supported)

If the question asks for "top N" or "first N" results, use: SELECT TOP N ...
Otherwise, generate query without any result limiting clauses.

Generate a valid InterSystems IRIS SQL query that answers the question."""

    try:
        # Call Ollama
        format = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Valid InterSystems IRIS SQL query without LIMIT or OFFSET"
                },
                "explanation": {
                    "type": "string",
                    "description": "Brief explanation of what the query does"
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
        logger.error(f"JSON decode error: {e}")
        return None, None
    except Exception as e:
        st.error(f"❌ Error generating query: {e}")
        logger.error(f"Query generation error: {e}")
        return None, None


def _render_query_result(query: str, explanation: str):
    """Render the generated query result"""
    
    # Validate and fix query for IRIS compatibility
    fixed_query, issues = _validate_and_fix_sql(query)
    
    # Show warning if query was modified
    if issues:
        st.warning("⚠️ Query adjusted for InterSystems IRIS compatibility:\n" + 
                   "\n".join(f"- {issue}" for issue in issues))
    
    st.success("✅ SQL Query Generated Successfully!")
    
    # Display the SQL query
    st.markdown("#### 📝 Generated SQL Query")
    st.code(fixed_query, language="sql")
    
    # Display the query explanation
    st.markdown("#### 📝 Query Explanation")
    st.write(explanation)
    
    # Execute and display results
    st.markdown("#### 📊 Query Result")
    
    try:
        result = st.session_state.iris_connection.fetch(fixed_query)
        
        if result is not None and not result.empty:
            st.dataframe(result, use_container_width=True)
            
            # Download option
            csv = result.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Results (CSV)",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv"
            )
        else:
            st.info("Query executed successfully but returned no results")
            
    except Exception as e:
        st.error(f"❌ Error executing query: {e}")
        logger.error(f"Query execution error: {e}")