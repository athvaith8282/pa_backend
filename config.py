import os 

PARNET_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PARNET_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)
SQLITE_DIR = os.path.join(DATA_DIR, "sqlite_db")
os.makedirs(SQLITE_DIR, exist_ok=True)
SQLITE_FILEPATH = os.path.join(SQLITE_DIR, "pa_agent_db.sqlite")

RETRIEVER_DATA_DIR = os.path.join(PARNET_DIR, 'retriever/data')
RETRIEVER_STATUS_FILE = os.path.join(RETRIEVER_DATA_DIR, "status_retriever.json")
VEC_DB_DIR = os.path.join(DATA_DIR, 'vectordb')
VEC_DB_PATH = os.path.join(VEC_DB_DIR, 'blogs_chroma_db')