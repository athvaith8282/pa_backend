
from fastapi import FastAPI, UploadFile, Form, File
from schemas import InferIn, InferOut, HistoryIn, HistoryOut
from fastapi.responses import StreamingResponse
from datetime import datetime
from contextlib import asynccontextmanager

from agent import MyGraph
from config import RETRIEVER_DATA_DIR, RETRIEVER_STATUS_FILE
from retriever.main import update_retriever
from logger_config import get_logger

logger = get_logger()
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
@app.post('/stream')
async def stream(infer: InferIn):
    return(
        StreamingResponse(pa_agent.stream_output(infer),media_type="text/event-stream")
    )

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    description: str = Form()
    ):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{RETRIEVER_DATA_DIR}/file_{timestamp}.pdf"
        with open(filename, 'wb') as f:
            f.write(await file.read())
        update_retriever(filename, description=description)
        return {
            "filename" : filename,
            "status" : "Updated"
        }
    except Exception as e:
        logger.exception(e)
        return {
            "filename" : filename,
            "status" : "Failed"
        }