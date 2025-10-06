
from fastapi import FastAPI, UploadFile, Form, File, Body
from schemas import InferIn, InferOut, HistoryIn, HistoryOut
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime
from contextlib import asynccontextmanager

from dotenv import load_dotenv
load_dotenv()

from agent import MyGraph
import config as cfg 
from retriever.main import update_retriever
from logger_config import get_logger

import json

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
        filename = f"{cfg.RETRIEVER_DATA_DIR}/file_{timestamp}.pdf"
        with open(filename, 'wb') as f:
            f.write(await file.read())
        update_retriever(filename, description=description)
        return {
            "filename" : filename,
            "status" : "Updated"
        }
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,  # HTTP error code
            content={
                "filename": filename,
                "status": "Failed",
                "error": str(e)
            }
        )

@app.post('/store-json')
def store_token(token: dict = Body(...)):
    try:
        with open(cfg.GOOGLE_TOKEN_PATH, 'w') as f:
            json.dump(token, f)
        return {
            "status" : "Updated"
        }
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content= {
                "status" : "Failed"
            }
        )

@app.get('/get-token')
def get_token():
    try:
        with open(cfg.GOOGLE_TOKEN_PATH, 'r') as f:
            response = json.load(f)
        return response
    except Exception as e:
        logger.exception(e)
        return JSONResponse(
            status_code=500,
            content= {
                "status" : "Failed"
            }
        )