from langgraph.graph import StateGraph, START, END, add_messages
from typing import TypedDict, Annotated, List
from langchain_core.messages import AIMessage

from sqlite_db import get_sqlite_conn
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import HumanMessage, messages_to_dict


from schemas import InferIn

class MyState(TypedDict):

    messages : Annotated[List, add_messages]

class MyGraph():

    def __init__(self):
        self.graph = None 
        self.sqlite_conn = None
        self.memory =None
    
    async def initiate(self):
        await self.compile_graph()

    def chatbot(self, state):
        return {
            "messages": AIMessage(content="Hello, How Can I help You Today!!")
        }
    
    async def compile_graph(self):
        graph_builder = StateGraph(MyState)
        graph_builder.add_node("chatbot", self.chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        self.sqlite_conn = await get_sqlite_conn()
        self.memory = AsyncSqliteSaver(conn=self.sqlite_conn)
        self.graph = graph_builder.compile(checkpointer=self.memory)
    
    async def get_history(self, thread_id):
        conf = {"configurable": {"thread_id": thread_id}}
        block = await self.memory.aget(conf)
        if block:
            history = block["channel_values"]["messages"]
            return messages_to_dict(history)
        else:    
            return []

    async def invoke(self, infer: InferIn):
        if self.graph:
            response = await self.graph.ainvoke({
                "messages": [
                    HumanMessage(content=infer.input)
                ]
            }, config={
                "configurable": {
                    "thread_id": str(infer.thread_id)
                }
            })
            return response
        else:
            return "Graph is not compiled"
    