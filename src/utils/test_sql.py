import os
import sqlite3
import re

def run_sql_tests(db_path, sql_script_path):
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Reading SQL script: {sql_script_path}")
    with open(sql_script_path, 'r') as f:
        sql_content = f.read()
        
    # Remove block comments (/* ... */) using regex
    sql_clean = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
    
    # Split by semicolon
    statements = sql_clean.split(';')
    
    print(f"Executing analytical SQL statements in SQLite...")
    
    success_count = 0
    fail_count = 0
    
    for idx, stmt in enumerate(statements):
        stmt_stripped = stmt.strip()
        if not stmt_stripped:
            continue
        
        # Check if it has a valid SQL start word
        lines = [line.strip() for line in stmt_stripped.split('\n') if line.strip() and not line.strip().startswith('--')]
        if not lines:
            continue
            
        first_line = lines[0]
        first_word = first_line.split()[0].upper()
        
        # Skip SQL Server / PLpgSQL commands that might fail in SQLite (e.g. standard procedure declarations)
        if first_word in ["CREATE", "SELECT", "WITH"]:
            print(f"\n[{success_count + fail_count + 1}] Executing: {first_word} statement...")
            try:
                cursor.execute(stmt_stripped)
                if first_word == "SELECT" or (first_word == "WITH" and "SELECT" in stmt_stripped.upper()):
                    # Print sample output
                    cols = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchmany(5)
                    print(f"Columns: {cols}")
                    for row in rows:
                        print(row)
                else:
                    conn.commit()
                    print("Statement executed successfully.")
                success_count += 1
            except Exception as e:
                print(f"ERROR executing query: {e}")
                print(stmt_stripped[:200] + "...")
                fail_count += 1
                
    conn.close()
    print(f"\nSQL Verification completed. Successful: {success_count}, Failed: {fail_count}")

if __name__ == "__main__":
    db_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "processed", "claims_analytics.db"))
    sql_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sql", "queries_analytics.sql"))
    run_sql_tests(db_file, sql_file)
