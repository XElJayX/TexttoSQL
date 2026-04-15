from app.rag.retriever import retrieve_relevant_tables
from app.llm.prompt_builder import build_prompt
import ollama

def generate_sql(question:str)-> str:
    schema_context = retrieve_relevant_tables(question)
    prompt = build_prompt(question, schema_context)

    #FOR DEBUG
    print("\n--- PROMPT SENT TO LLM ---"
          f"\n{prompt}\n"
          "-------------------------\n")
    
    response = ollama.chat(
        model="llama3.2",
        messages=[{"role": "user", "content" :prompt}]
    )
    print("\n--- RESPONSE FROM LLM ---"
          f"\n{response.message.content}\n"
          "-------------------------\n")
    sql = response.message.content.strip()

    keywords = ["SELECT", "FROM", "WHERE", "UPDATE", "DELETE", "WITH", "INSERT"]

    for key in keywords:
       idx = sql.upper().find(key)
         if idx != -1:
            sql = sql[idx:]
            break
    return sql
    