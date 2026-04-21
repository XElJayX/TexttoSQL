def build_prompt(question:str, schema_context:str)-> str:
    return f"""You are a SQL expert. Given the following database schema, 
    write a PostgreSQL query to answer the user's question.

    SCHEMA:
    {schema_context}

    RULES:
    - Only use tables and columns that exist in the schema above
    - Output only valid PostgreSQL syntax, no comments, no explanation text, no natural language mixed into the query
    - Return only the SQL query, no explanation
    - Use table aliases for readability
    - Every column in SELECT that is not inside an aggregate function must appear in GROUP BY
    - If the question is ambiguous, make reasonable assumptions based on the schema
    - Prefer simple queries over complex ones. If the answer is in one table, do not join other tables.
    - Always define a table alias before using it
    - Use consistent aliases throughout the query. For example, if you alias the companies table as c, use c to refer to it everywhere in the query.
    - Never use aggregate functions in WHERE clauses, use HAVING instead 
    - Use exact values as they appear in the sample data rows provided
  


    QUESTION:
    {question}

    SQL:"""