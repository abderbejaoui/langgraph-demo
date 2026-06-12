from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_anthropic import ChatAnthropic
from langchain_tavily import TavilySearch
import dotenv

dotenv.load_dotenv()

# 1. State
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Tools + model
search = TavilySearch(max_results=2)
tools = [search]
llm = ChatAnthropic(model="claude-sonnet-4-6").bind_tools(tools)

# 3. Nodes
def call_model(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

def should_continue(state: State):
    if state["messages"][-1].tool_calls:
        return "tools"
    return "end"

# 4. Build graph
graph = StateGraph(State)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue,
    {"tools": "tools", "end": END})
graph.add_edge("tools", "agent")
app = graph.compile()

# 5. Run it
if __name__ == "__main__":
    question = "what is the recent model released by anothropic in 2026?"
    print(f"\n=== USER QUESTION ===\n{question}\n")

    final_state = None
    for step, update in enumerate(
        app.stream({"messages": [{"role": "user", "content": question}]}),
        start=1,
    ):
        for node_name, node_output in update.items():
            last = node_output["messages"][-1]
            print(f"--- STEP {step}: node '{node_name}' ---")
            if node_name == "agent":
                if getattr(last, "tool_calls", None):
                    for tc in last.tool_calls:
                        print(f"  -> tool call: {tc['name']}({tc['args']})")
                else:
                    print("  -> produced final answer")
            elif node_name == "tools":
                preview = str(last.content)[:200].replace("\n", " ")
                print(f"  -> tool result (preview): {preview}...")
            final_state = node_output

    print("\n=== FINAL ANSWER ===")
    print(final_state["messages"][-1].content)
