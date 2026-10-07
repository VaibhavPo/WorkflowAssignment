import sqlite3
import os
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

# Path to the sqlite database
DB_PATH = Path(__file__).parent.parent / "data" / "orders.db"

def _init_db():
    """Initializes the database with mock data if it doesn't exist."""
    db_dir = DB_PATH.parent
    db_dir.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_email TEXT,
        customer_name TEXT,
        order_date TEXT,
        order_status TEXT,
        total_amount REAL
    )
    ''')
    
    # Create shipments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shipments (
        order_id TEXT PRIMARY KEY,
        shipment_status TEXT,
        tracking_number TEXT,
        carrier TEXT,
        estimated_delivery TEXT,
        FOREIGN KEY(order_id) REFERENCES orders(order_id)
    )
    ''')
    
    # Create employees table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        employee_id TEXT PRIMARY KEY,
        employee_name TEXT,
        skills TEXT,
        current_workload REAL,
        capacity REAL,
        availability TEXT
    )
    ''')
    
    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM orders")
    if cursor.fetchone()[0] == 0:
        orders_data = [
            ("ORD-1001", "alice@example.com", "Alice Smith", "2023-10-01", "Processing", 150.0),
            ("ORD-1002", "bob@example.com", "Bob Jones", "2023-10-02", "Shipped", 200.0),
            ("ORD-1003", "charlie@example.com", "Charlie Brown", "2023-10-03", "Delivered", 300.0)
        ]
        cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", orders_data)
        
        shipments_data = [
            ("ORD-1002", "In Transit", "TRK123456789", "FedEx", "2023-10-05"),
            ("ORD-1003", "Delivered", "TRK987654321", "UPS", "2023-10-04")
        ]
        cursor.executemany("INSERT INTO shipments VALUES (?, ?, ?, ?, ?)", shipments_data)
        
        conn.commit()
        
    cursor.execute("SELECT COUNT(*) FROM employees")
    if cursor.fetchone()[0] < 9: # if not fully populated
        # Clear existing to re-populate
        cursor.execute("DELETE FROM employees")
        
        employees_data = [
            ("E101", "Alice Smith", "python, sql, llm, fastapi", 0.1, 1.0, "Available"),
            ("E102", "Bob Jones", "python, excel, sql", 0.2, 1.0, "Available"),
            ("E103", "Charlie Brown", "python, react, typescript", 0.5, 1.0, "Available"),
            ("E104", "Diana Prince", "docker, sql, python, react", 0.3, 1.0, "Available"),
            ("E105", "Evan Wright", "excel-processing, data-entry", 0.4, 1.0, "Available"),
            ("E106", "Fiona Gallagher", "kubernetes, docker, aws, rust", 0.2, 1.0, "Available"),
            ("E107", "George Martin", "seo, copywriting, keywords", 0.1, 1.0, "Available"),
            ("E108", "Hannah Abbott", "aws, python, sql, llm-integration", 0.3, 1.0, "Available"),
            ("E109", "Ian Malcolm", "product-management, agile", 0.8, 1.0, "Busy")
        ]
        cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)", employees_data)
        conn.commit()
    
    conn.close()

def query_sqlite(query: str, params: Tuple = ()) -> Dict[str, Any]:
    """
    Executes a parameterized query against the SQLite database.
    
    Args:
        query: The SQL query string (e.g. "SELECT * FROM orders WHERE order_id = ?").
        params: A tuple of parameters to bind to the query.
        
    Returns:
        Dict with 'status', 'data' (list of dicts), and 'error' (if any).
    """
    _init_db()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Return dict-like rows
        cursor = conn.cursor()
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        result = [dict(row) for row in rows]
        
        # If it was an INSERT/UPDATE/DELETE, commit the transaction
        if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
            conn.commit()
            
        conn.close()
        
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
