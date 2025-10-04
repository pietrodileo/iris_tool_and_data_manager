# utils/data_analysis.py
"""
Data Analysis Utilities
Functions for data profiling, filtering, and transformation
"""

import pandas as pd
from typing import Dict, Any, List

def generate_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive data profile statistics
    
    Args:
        df: pandas DataFrame to profile
        
    Returns:
        Dictionary containing overview and column-level statistics
    """
    profile = {
        'overview': {
            'rows': len(df),
            'columns': len(df.columns),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
            'duplicates': df.duplicated().sum()
        },
        'columns': {}
    }
    
    for col in df.columns:
        col_info = {
            'dtype': str(df[col].dtype),
            'missing': df[col].isna().sum(),
            'missing_pct': f"{(df[col].isna().sum() / len(df) * 100):.1f}%",
            'unique': df[col].nunique(),
            'unique_pct': f"{(df[col].nunique() / len(df) * 100):.1f}%"
        }
        
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info.update({
                'mean': f"{df[col].mean():.2f}" if not df[col].isna().all() else "N/A",
                'std': f"{df[col].std():.2f}" if not df[col].isna().all() else "N/A",
                'min': f"{df[col].min():.2f}" if not df[col].isna().all() else "N/A",
                'max': f"{df[col].max():.2f}" if not df[col].isna().all() else "N/A",
                'median': f"{df[col].median():.2f}" if not df[col].isna().all() else "N/A"
            })
        else:
            top_values = df[col].value_counts().head(3)
            col_info['top_values'] = dict(top_values)
        
        profile['columns'][col] = col_info
    
    return profile

def apply_filters(df: pd.DataFrame, filters: Dict[str, Dict]) -> pd.DataFrame:
    """
    Apply dynamic filters to dataframe
    
    Args:
        df: DataFrame to filter
        filters: Dictionary of filter configurations
        
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    for col, filter_config in filters.items():
        if filter_config['type'] == 'numeric':
            min_val, max_val = filter_config['range']
            filtered_df = filtered_df[
                (filtered_df[col] >= min_val) & 
                (filtered_df[col] <= max_val)
            ]
        elif filter_config['type'] == 'categorical':
            if filter_config['selected']:
                filtered_df = filtered_df[
                    filtered_df[col].isin(filter_config['selected'])
                ]
        elif filter_config['type'] == 'text':
            if filter_config['search']:
                filtered_df = filtered_df[
                    filtered_df[col].astype(str).str.contains(
                        filter_config['search'], 
                        case=False, 
                        na=False
                    )
                ]
    
    return filtered_df

def get_numeric_columns(df: pd.DataFrame) -> List[str]:
    """Get list of numeric column names"""
    return df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()

def get_categorical_columns(df: pd.DataFrame) -> List[str]:
    """Get list of categorical column names"""
    return df.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()

def aggregate_data(df: pd.DataFrame, group_cols: List[str], agg_col: str, agg_func: str) -> pd.DataFrame:
    """
    Perform group by aggregation
    
    Args:
        df: DataFrame to aggregate
        group_cols: Columns to group by
        agg_col: Column to aggregate
        agg_func: Aggregation function (sum, mean, count, min, max, std)
        
    Returns:
        Aggregated DataFrame
    """
    grouped = df.groupby(group_cols)[agg_col].agg(agg_func).reset_index()
    grouped.columns = group_cols + [f"{agg_col}_{agg_func}"]
    return grouped

def create_calculated_column(df: pd.DataFrame, new_col_name: str, col1: str, operation: str, col2: str) -> pd.DataFrame:
    """
    Create a new calculated column based on two existing columns
    
    Args:
        df: DataFrame to add column to
        new_col_name: Name for the new column
        col1: First column name
        operation: Operation (+, -, *, /)
        col2: Second column name
        
    Returns:
        DataFrame with new column
    """
    new_df = df.copy()
    
    if operation == "+":
        new_df[new_col_name] = new_df[col1] + new_df[col2]
    elif operation == "-":
        new_df[new_col_name] = new_df[col1] - new_df[col2]
    elif operation == "*":
        new_df[new_col_name] = new_df[col1] * new_df[col2]
    elif operation == "/":
        new_df[new_col_name] = new_df[col1] / new_df[col2]
    
    return new_df