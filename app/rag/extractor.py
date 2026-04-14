#Interesting file, Introspects the DB and builds a rich text description of each table
from app.db.connection import get_connection

def extract_schema():
    conn = get_connection()
    cur = conn.cursor()

    #GET ALL TABLES IN THE PUBLIC SCHEMA
    cur.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema='public' AND table_type='BASE TABLE'
    ORDER BY table_name
    """)

    tables = [row[0] for row in cur.fetchall()]

    schema_chunks = []

    for table in tables:
        # GET COLUMNS WITH TYPES AND NULLABLE INFO
        cur.execute("""
        SELECT column_name,data_type,is_nullable
        FROM information_schema.columns
        WHERE table_name=%s AND table_schema='public'
        ORDER BY ordinal_position
        """,(table,))

        columns=cur.fetchall()

        #get foreign keys
        cur.execute("""
        SELECT kcu.column_name, ccu.table_name AS foreign_table
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
        ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
        on ccu.constraint_name = tc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name=%s
        """,(table,))

        foreign_keys = cur.fetchall()

        #get 3 sample row to help LLM understand

        cur.execute(f"SELECT * FROM {table} LIMIT 3")
        sample_rows = cur.fetchall()
        col_names = [desc[0] for desc in cur.description]

        #BUILD human readable text description of the table
        chunk = f"Table: {table}\n"
        chunk += "Columns:\n"
        for col_name, data_type, nullable in columns:
            null_str = "nullable" if nullable=="YES" else "not nullable"
            chunk += f"  - {col_name} ({data_type}, {null_str})\n"
        
        if foreign_keys:
            chunk += "Relationships:\n"
            for col, ref_table in foreign_keys:
                chunk += f"  - {col} references {ref_table}.id\n"
        
        if sample_rows:
            chunk += "Sample data:\n"
            for row in sample_rows:
                row_dict = dict(zip(col_names, row))
                # Truncate long values so chunks stay compact
                row_str = {k: str(v)[:50] for k, v in row_dict.items()}
                chunk += f"  {row_str}\n"
        schema_chunks.append({
            "table_name": table,
            "chunk": chunk
        })

    cur.close()
    conn.close()
    return schema_chunks


if __name__ == "__main__":
    chunks = extract_schema()
    for c in chunks:
        print(f"\n{'='*50}")
        print(c["chunk"])
