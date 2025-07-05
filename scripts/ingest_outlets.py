# scripts/ingest_outlets.py
import sqlite3
import pandas as pd
import os

print("Starting outlets ingestion process...")

# --- 1. Define File Paths ---
# Use os.path.join for cross-platform compatibility
base_dir = os.path.dirname(__file__)
csv_file_path = os.path.join(base_dir, '..', 'data', 'zus_outlets.csv')
db_path = os.path.join(base_dir, '..', 'db', 'outlets.db')

# --- 2. Read Data from CSV ---
print(f"Reading outlet data from {csv_file_path}")
try:
    # Use pandas to easily read the CSV
    df = pd.read_csv(csv_file_path)
    # Basic data cleaning: remove leading/trailing whitespace from all string columns
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    print("CSV data loaded successfully into pandas DataFrame:")
    print(df.head())
except FileNotFoundError:
    print(f"Error: The file {csv_file_path} was not found.")
    exit()

# --- 3. Create SQLite Database and Table ---
# Connect to the SQLite database (this will create the file if it doesn't exist)
print(f"Connecting to and creating SQLite database at {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Define the table name
table_name = 'outlets'

# Drop the table if it already exists to ensure a fresh start
print(f"Dropping table '{table_name}' if it exists...")
cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

# Create the table with a suitable schema
# Using TEXT for all columns is simple and flexible for this use case.
print(f"Creating new table '{table_name}'...")
cursor.execute(f'''
CREATE TABLE {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outlet_name TEXT,
    address TEXT,
    operating_hours TEXT,
    services TEXT
)
''')
print("Table created successfully.")

# --- 4. Insert Data into the Table ---
print(f"Inserting {len(df)} rows into '{table_name}' table...")
# Use pandas' to_sql() function for easy insertion
# 'if_exists='append'' adds the data to the table
# 'index=False' prevents pandas from writing the DataFrame index as a column
df.to_sql(table_name, conn, if_exists='append', index=False)

print("Data inserted successfully.")

# --- 5. Verify the Insertion ---
print("Verifying inserted data by fetching the first 5 rows:")
cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
rows = cursor.fetchall()
for row in rows:
    print(row)

# Commit the changes and close the connection
conn.commit()
conn.close()

print("\nIngestion complete! SQLite database 'outlets.db' has been created and populated.")