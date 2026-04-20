from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.models import QueryRequest, QueryResponse
from app.rag.retriever import retrieve_with_metadata
from app.llm.sql_generator import generate_sql
from app.db.connection import get_connection

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query", response_model=QueryResponse)
async def query(query:QueryRequest) -> QueryResponse:
    try:
        retrieved_data = retrieve_with_metadata(query.question)
        sql = generate_sql(query.question, schema_context=retrieved_data["chunks"])
    except Exception as e:
        return QueryResponse(success=False, error=str(e))
    if query.execute:
        try:
            conn=get_connection()
            cur=conn.cursor()
            cur.execute(sql)
            results = cur.fetchall() if cur.description else []
            return QueryResponse(sql=sql, results=results, success=True, retrieved_tables=retrieved_data["tables"], columns=[desc[0] for desc in cur.description] if cur.description else None)
        except Exception as e:
            return QueryResponse(sql=sql, success=False, error=str(e), retrieved_tables=retrieved_data["tables"])
        finally:
            cur.close()
            conn.close()   
    else:
        return QueryResponse(sql=sql, success=True, retrieved_tables=retrieved_data["tables"])