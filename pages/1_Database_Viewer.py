import streamlit as st
import sqlite3
import pandas as pd
import os
from pathlib import Path

st.set_page_config(page_title="Database Viewer", layout="wide")
st.title("Database Viewer")
st.markdown("View the underlying SQLite database and execution logs.")

db_path = Path(os.getcwd()) / "data" / "orders.db"
logs_path = Path(os.getcwd()) / "workflow_execution_logs.csv"

st.header("SQLite Database (`orders.db`)")
if not db_path.exists():
    st.error(f"Database not found at {db_path}")
else:
    try:
        conn = sqlite3.connect(db_path)
        
        # Get all tables
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        
        if not tables:
            st.warning("No tables found in the database.")
        else:
            # Create tabs for each table
            tabs = st.tabs(tables)
            
            for i, table in enumerate(tables):
                with tabs[i]:
                    st.subheader(f"Table: {table}")
                    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                    st.dataframe(df, use_container_width=True)
                    st.caption(f"Total rows: {len(df)}")
                    
        conn.close()
    except Exception as e:
        st.error(f"Error reading database: {e}")

st.divider()

st.header("Workflow Execution Logs")
if not logs_path.exists():
    st.info("No execution logs found yet.")
else:
    try:
        logs_df = pd.read_csv(logs_path)
        st.dataframe(logs_df, use_container_width=True)
        st.caption(f"Total logs: {len(logs_df)}")
    except Exception as e:
        st.error(f"Error reading logs: {e}")
