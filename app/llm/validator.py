#LVL 1 Safety Check
#LVL 2 Syntax Check
import re
from app.db.connection import get_connection

def validate_sql(sql:str) -> tuple[bool, str]:
    
    #LVL 1: Safety check
    forbidden_keywords = ["DROP", "ALTER", "TRUNCATE", "CREATE", "GRANT", "REVOKE", "EXECUTE"]
    sql_upper = sql.upper()
    for keyword in forbidden_keywords:
        if re.search(rf'\b{keyword}\b', sql_upper):
            return False, f"Forbidden keyword detected: {keyword}"
    
    
    #LVL 2: Basic syntax check
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"EXPLAIN {sql}")
    except Exception as e:
        return False, f"Syntax error: {str(e)}"
    finally:
        cur.close()
        conn.close()
    
    return True, "SQL is valid and safe"

    
if __name__ == "__main__":
    tests = [
        "SELECT * FROM companies",
        "DROP TABLE companies",
        "SELECT * FROM nonexistent_table",
        "DELETE FROM users WHERE id = '123'",
    ]
    for sql in tests:
        valid, msg = validate_sql(sql)
        print(f"{'OK' if valid else 'FAIL'} | {msg} | {sql[:50]}")