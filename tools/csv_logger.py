import csv
import os
from filelock import FileLock
from typing import Optional

def log_workflow_execution(
    log_file_path: str,
    execution_id: str,
    workflow_id: str,
    timestamp: str,
    status: str,
    failed_step: str,
    error: str,
    execution_time: float,
    slowest_step: str,
    slowest_step_sec: float
):
    """
    Appends a workflow execution log to a CSV file concurrently.
    Uses filelock to prevent race conditions during concurrent writes.
    """
    file_exists = os.path.isfile(log_file_path)
    lock_path = f"{log_file_path}.lock"
    lock = FileLock(lock_path, timeout=10) # 10 seconds timeout

    try:
        with lock:
            with open(log_file_path, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                # Write header if file does not exist
                if not file_exists:
                    writer.writerow([
                        "execution_id", 
                        "workflow_id", 
                        "timestamp", 
                        "status", 
                        "failed_step",
                        "error",
                        "execution_time",
                        "slowest_step",
                        "slowest_step_sec"
                    ])
                
                writer.writerow([
                    execution_id,
                    workflow_id,
                    timestamp,
                    status,
                    failed_step,
                    error,
                    execution_time,
                    slowest_step,
                    slowest_step_sec
                ])
    except Exception as e:
        print(f"Failed to log execution: {e}")
