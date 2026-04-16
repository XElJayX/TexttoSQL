from app.rag.retriever import retrieve_relevant_tables
from app.llm.prompt_builder import build_prompt
from app.llm.validator import validate_sql
import ollama


def generate_sql(question: str) -> str:
    schema_context = retrieve_relevant_tables(question)
    prompt = build_prompt(question, schema_context)

    # FOR DEBUG
    print(
        "\n--- PROMPT SENT TO LLM ---"
        f"\n{prompt}\n"
        "-------------------------\n"
    )

    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )

    print(
        "\n--- RESPONSE FROM LLM ---"
        f"\n{response.message.content}\n"
        "-------------------------\n"
    )

    sql = response.message.content.strip()

    keywords = ["SELECT", "FROM", "WHERE", "UPDATE", "DELETE", "WITH", "INSERT"]

    for key in keywords:
        idx = sql.upper().find(key)
        if idx != -1:
            sql = sql[idx:]
            break

    valid, msg = validate_sql(sql)

    if not valid:
        fix_prompt = f"""The SQL query you generated has an error:

SQL: {sql}
ERROR: {msg}

Fix the SQL and return only the corrected query."""

        response = ollama.chat(
            model="llama3.2",
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": sql},
                {"role": "user", "content": fix_prompt},
            ],
        )

        sql = response.message.content.strip()
        valid, msg = validate_sql(sql)

        if not valid:
            raise ValueError(
                f"LLM failed to generate valid SQL after correction attempt. Last error: {msg}"
            )

    return sql


if __name__ == "__main__":
    questions = [
        "which companies have cancelled their subscriptions?",
        "what is the total revenue by plan?",
        "which users have never logged in?",
    ]

    for q in questions:
        print(f"\nQuestion: {q}")
        try:
            sql = generate_sql(q)
            print(f"Generated SQL:\n{sql}")
        except ValueError as e:
            print(f"Failed: {e}")
        print("=" * 60)