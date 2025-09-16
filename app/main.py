from typing import TypedDict, List
from dotenv import load_dotenv
import os

from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from models import model_sonnet_37
from tools import get_customer_info


# Load environment variables
load_dotenv()

# Shared LLM
llm = model_sonnet_37

# Shared tool
search_tool = DuckDuckGoSearchRun()



analyzer_agent = create_react_agent(
    model=llm,
    tools=[get_customer_info],
    prompt="You are a expert financial helper, analyze the user data obtained from his bank statements. Create a Report that guesses what is the user financial situation, if it is healthy, what are the main components of his spending habits and how can he improve his situation." 
)


# Create two different ReAct agents
travel_agent = create_react_agent(
    model=llm,
    tools=[search_tool],
    prompt="You are a travel assistant that helps users discover places and destinations."
)

planner_agent = create_react_agent(
    model=llm,
    tools=[search_tool],
    prompt="You are a planning assistant that helps users organize their itinerary."
)

# Define LangGraph state
class AgentState(TypedDict):
    messages: List

# Wrap each agent in a node function
def run_analyzer_agent(state: AgentState) -> AgentState:
    result = analyzer_agent.invoke(state)
    return {"messages": result["messages"]}

def run_travel_agent(state: AgentState) -> AgentState:
    result = travel_agent.invoke(state)
    return {"messages": result["messages"]}

def run_planner_agent(state: AgentState) -> AgentState:
    result = planner_agent.invoke(state)
    return {"messages": result["messages"]}

# Build the graph
graph = StateGraph(AgentState)

# Add nodes
graph.add_node("analyzer_agent", run_analyzer_agent)
graph.add_node("planner_agent", run_planner_agent)

# Connect nodes
graph.add_edge(START, "analyzer_agent")
graph.add_edge("analyzer_agent", "planner_agent")
graph.add_edge("planner_agent", END)

# Compile
app = graph.compile()

# Run the graph
initial_input = {"messages": [HumanMessage(content="Analyze user history of Noah Rhodes")]}
result = app.invoke(initial_input)

# Print the output
for msg in result["messages"]:
    if hasattr(msg, "content"):
        print(f"{msg.type.upper()}: {msg.content}")