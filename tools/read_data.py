import os
import pandas as pd
import numpy as np
from typing import Dict, Any, Union

from tools.column_normalizer import apply_column_mapping

def read_data(file_path: Union[str, os.PathLike]) -> Dict[str, Any]:
    """
    Reads structured business data from CSV or XLSX files for workflow automation.
    
    This tool is generic and can be used by any workflow (e.g., WF001-WF011) 
    without modification. It gracefully handles errors, missing files, and 
    unsupported formats.
    
    Args:
        file_path: Path to the CSV or XLSX file.
        
    Returns:
        A dictionary containing:
        - columns (list): List of normalized column names.
        - row_count (int): Number of rows in the data.
        - records (list): List of dictionaries representing the data (records).
        - file_type (str): Detected file format ('csv' or 'xlsx').
        - metadata (dict): Dictionary of basic file metadata (e.g., file_size_bytes, file_name).
        
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file format is unsupported, the file is empty, or malformed.
    """
    file_path_str = str(file_path)
    
    # 1. Validate file existence and type
    if not os.path.exists(file_path_str):
        raise FileNotFoundError(f"File not found: {file_path_str}")
        
    if not os.path.isfile(file_path_str):
        raise ValueError(f"Path is not a regular file: {file_path_str}")
        
    # 2. Check for empty files
    file_size = os.path.getsize(file_path_str)
    if file_size == 0:
        raise ValueError(f"File is empty: {file_path_str}")
        
    ext = os.path.splitext(file_path_str)[1].lower()
    
    # 3. Read data based on format
    try:
        if ext == '.csv':
            df = pd.read_csv(file_path_str)
            file_type = 'csv'
        elif ext in ['.xlsx', '.xls']:
            # openpyxl is appropriate for .xlsx, xlrd (or default) for .xls
            engine = 'openpyxl' if ext == '.xlsx' else None
            df = pd.read_excel(file_path_str, engine=engine)
            file_type = 'xlsx' if ext == '.xlsx' else 'xls'
        else:
            raise ValueError(f"Unsupported file format: {ext}. Only CSV and XLSX are supported.")
            
    except pd.errors.EmptyDataError:
        raise ValueError(f"File is empty or malformed: {file_path_str}")
    except Exception as e:
        raise ValueError(f"Failed to read file {file_path_str}: {str(e)}") from e
        
    # 4. Normalize columns using the new column_normalizer
    df, mapping, unresolved = apply_column_mapping(df)
    
    # 5. Handle missing values for better serialization (JSON compatibility)
    df = df.replace({np.nan: None})
    
    records = df.to_dict(orient="records")
    
    return {
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "records": records,
        "file_type": file_type,
        "metadata": {
            "file_name": os.path.basename(file_path_str),
            "file_size_bytes": file_size,
        },
        "column_mapping": mapping,
        "unresolved_columns": unresolved
    }
