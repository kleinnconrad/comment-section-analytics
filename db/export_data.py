import sqlite3
import pandas as pd
import os

def export_database_to_csv(db_path, output_folder):
    """
    Reads an SQLite database, converts each table to a Pandas DataFrame,
    and saves them as CSV files in the specified output folder.
    
    Args:
        db_path (str): The path to the SQLite database.
        output_folder (str): The folder to output the CSVs.
    """
    # Create the output data folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    
    # Get a list of all tables in the database
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"Found tables: {', '.join(tables)}")
    
    # Export each table to a CSV file
    for table in tables:
        print(f"Loading '{table}' into DataFrame...")
        # Read table into a Pandas DataFrame
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        
        # Save DataFrame to CSV
        output_path = os.path.join(output_folder, f"{table}.csv")
        print(f"Saving '{table}' to {output_path}...")
        df.to_csv(output_path, index=False)
        
    conn.close()
    print("All tables have been successfully exported!")

if __name__ == "__main__":
    # Get the directory of this script (the 'db' folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # DB is now in the same folder as the script
    DB_FILE = os.path.join(script_dir, "corpus.sqlite3")
    
    # Output 'data' folder is in the parent directory
    OUT_DIR = os.path.join(os.path.dirname(script_dir), "data")
    
    if os.path.exists(DB_FILE):
        export_database_to_csv(DB_FILE, OUT_DIR)
    else:
        print(f"Error: Database file '{DB_FILE}' not found in the current directory.")
