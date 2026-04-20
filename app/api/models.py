from pydantic import BaseModel
from typing import Optional
class QueryRequest(BaseModel):
    question: str
    execute: Optional[bool] = True

class QueryResponse(BaseModel):
    sql: str
    results: Optional[list[list]] = None
    success: bool
    error: Optional[str] = None
    retrieved_tables: Optional[list[str]] = None