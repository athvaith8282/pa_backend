from pydantic import BaseModel
from uuid import UUID

class Infer(BaseModel):
    thread_id : UUID

class InferIn(Infer):
    input : str

class InferOut(Infer):
    text: str

class HistoryIn(Infer):
    pass 

class HistoryOut(Infer):
    messages : list