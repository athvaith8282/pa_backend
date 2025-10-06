from langgraph.graph import StateGraph, START, END
from sqlite_db import get_sqlite_conn
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import HumanMessage, messages_to_dict
from langgraph.prebuilt import tools_condition, ToolNode

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.load import dumps

from my_state import MyState
from my_tools import get_tools
from schemas import InferIn

class MyGraph():

    def __init__(self):
        self.graph = None 
        self.sqlite_conn = None
        self.memory =None
    
    async def initiate(self):
        await self.compile_graph()

    def chatbot(self, state):
        return {
            "messages": self.llm_with_tools.invoke(state["messages"])
        }
    
    async def compile_graph(self):

        self.tools = await get_tools()
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        graph_builder = StateGraph(MyState)
        graph_builder.add_node("chatbot", self.chatbot)

        tool_node = ToolNode(self.tools)
        graph_builder.add_node("tools", tool_node)

        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_conditional_edges("chatbot", tools_condition, path_map={
            "tools": "tools",
            END: END
        })
        graph_builder.add_edge("tools", "chatbot")
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
    
    async def stream_output(self, infer: InferIn):
        if self.graph:
            async for event in self.graph.astream_events(
                {
                    "messages": [HumanMessage(content=infer.input)]
                },
                config={
                "configurable": {
                    "thread_id": str(infer.thread_id)
                }
            }):
                yield dumps(event) + '\n'