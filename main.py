
from fastapi import FastAPI
from schemas import InferIn, InferOut, HistoryIn, HistoryOut

from contextlib import asynccontextmanager

from agent import MyGraph

pa_agent: MyGraph | None  = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pa_agent
    pa_agent = MyGraph()
    await pa_agent.initiate()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/')
async def root():
    return {
        "Welcome": "Hello User"
    }

@app.post('/history', response_model=HistoryOut)
async def history(history: HistoryIn):
    response = await pa_agent.get_history(
        thread_id=history.thread_id
    )

    return HistoryOut(
        thread_id=history.thread_id,
        messages=response
    )

@app.post('/invoke', response_model=InferOut)
async def invoke(infer: InferIn):
    response = await pa_agent.invoke(
       infer
    )
    return InferOut(
        thread_id=infer.thread_id,
        text=response["messages"][-1].content
    )