# IRIS Tool and Data Manager

A comprehensive Python toolkit for integrating pandas DataFrames with InterSystems IRIS databases, featuring a Streamlit-based data management interface.

## Overview

This project demonstrates seamless integration between InterSystems IRIS and the Python data science ecosystem. It consists of two main components:

1. **IRIStool**: A Python module providing a high-level API for IRIS database operations
2. **IRIS Data Manager**: A Streamlit web application for visual data management and analysis

## Installation

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git

### Setup Steps

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/iris_tool_and_data_manager.git
cd iris_tool_and_data_manager
```

2. **Create and activate virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Start InterSystems IRIS with Docker**

```bash
docker-compose up -d
```

5. **Configure environment variables**

Create a `.env` file in the project root:

```env
IRIS_HOST=127.0.0.1
IRIS_PORT=1972
IRIS_NAMESPACE=USER
IRIS_USER=_SYSTEM
IRIS_PASSWORD=SYS
```

6. **Run the application**

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## IRIStool Module

The `IRIStool` class provides a pandas-friendly interface to InterSystems IRIS databases with support for:

- DataFrame to table conversion with automatic type inference
- CRUD operations (Create, Read, Update, Delete)
- Index management (standard, HNSW vector indexes)
- View creation and management
- Schema exploration

### Quick Start Example

```python
import pandas as pd
from utils.iristool import IRIStool

# Initialize connection
with IRIStool(
    host="127.0.0.1",
    port=1972,
    namespace="USER",
    username="_SYSTEM",
    password="SYS"
) as iris:
    
    # Create sample DataFrame
    df = pd.DataFrame({
        "ID": [1, 2, 3],
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [30, 25, 35],
        "City": ["New York", "London", "Paris"]
    })
    
    # Convert DataFrame to IRIS table
    iris.df_to_table(
        df=df,
        table_name="Employees",
        table_schema="Company",
        primary_key="ID",
        exist_ok=True,
        drop_if_exists=True,
        indices=[
            {"column": "Age", "type": "index"},
            {"column": "Name", "type": "unique"}
        ]
    )
    
    # Query data back
    result = iris.fetch("SELECT * FROM Company.Employees WHERE Age > ?", [28])
    print(result)
    
    # Insert new records
    iris.insert_many(
        table_name="Employees",
        table_schema="Company",
        rows=[
            {"ID": 4, "Name": "Diana", "Age": 28, "City": "Rome"},
            {"ID": 5, "Name": "Ethan", "Age": 32, "City": "Tokyo"}
        ]
    )
    
    # Update records
    iris.update(
        table_name="Employees",
        table_schema="Company",
        new_values={"City": "San Francisco"},
        filters={"ID": 1}
    )
    
    # Create a view
    iris.create_view(
        view_name="AvgAgeByCity",
        view_schema="Company",
        sql="SELECT City, AVG(Age) as AvgAge FROM Company.Employees GROUP BY City"
    )
    
    # Explore namespace
    tables = iris.show_namespace_tables(table_schema="Company")
    print(tables)
```

### Key Features

**Automatic Type Inference**: The module intelligently maps pandas dtypes to IRIS SQL types:

- Integer types → INT/BIGINT
- Float types → DOUBLE
- Datetime → DATE/TIME/DATETIME
- Strings → VARCHAR/CLOB (based on length)
- Boolean → BIT

**Vector Search Support**: Create HNSW indexes for similarity search:

```python
iris.create_hnsw_index(
    table_name="Documents",
    column_name="Embedding",
    index_name="doc_vector_idx",
    distance="Cosine",
    M=16,
    ef_construct=200
)
```

**Context Manager Support**: Automatic connection cleanup:

```python
with IRIStool() as iris:
    # Your operations here
    pass
# Connection automatically closed
```

## IRIS Data Manager UI

The Streamlit-based interface provides a visual way to interact with your IRIS database without writing code.

### Features

#### 1. Connection Management (Sidebar)

- Configure connection parameters (host, port, namespace, credentials)
- Test connection with real-time feedback
- Default values loaded from `.env` file
- Connection status indicator

#### 2. Upload Data Tab

Upload and import data from various formats:

- **Supported formats**: CSV, Excel (XLSX/XLS), JSON, Parquet
- **Pre-import preview**: View data before saving
- **Data transformation**: 

  - Rename columns
  - Change data types
  - Handle missing values
- **Schema configuration**:
  - Specify table name and schema
  - Define primary key
  - Create indexes (standard, unique, HNSW for vectors)
- **Conflict resolution**: Choose to append or replace existing tables

#### 3. Explore & Analyze Tab

Comprehensive data exploration and analysis:

**a) Table Selection**

- Browse available schemas
- Select tables from dropdown
- View table metadata (row count, columns, indexes)

**b) Data Viewing**

- Paginated table display
- Column type information
- Row count statistics

**c) Filtering & Visualization**

- Apply filters on multiple columns (text, numeric, date)
- Export filtered results as CSV
- Create visualizations:
  - Bar charts for categorical data
  - Line charts for time series
  - Scatter plots for correlations
  - Histograms for distributions

**d) Aggregations**

- Group by single or multiple columns
- Apply aggregate functions (COUNT, SUM, AVG, MIN, MAX)
- Visualize aggregated results

**e) Text-to-SQL**

- Natural language query interface
- AI-powered SQL generation
- Execute generated queries
- View and download results

### Usage Workflow

1. **Connect**: Configure and test database connection in sidebar
2. **Upload**: Import data files or create tables manually
3. **Explore**: Browse existing tables and examine structure
4. **Analyze**: Apply filters, create visualizations, run aggregations
5. **Query**: Use natural language or SQL to extract insights

## Use Cases

- **Data Migration**: Easily move data between pandas and IRIS
- **Prototyping**: Quickly test data models before production
- **Analytics**: Combine pandas processing with IRIS storage
- **Vector Search**: Build semantic search applications with HNSW indexes
- **Data Exploration**: Visual interface for non-technical users
- **ETL Workflows**: Transform and load data into IRIS