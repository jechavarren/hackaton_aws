from typing import TypedDict, List
from dotenv import load_dotenv
import os

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from models import model_sonnet_37, model_haiku_3
from tools import get_customer_info, get_customer_current_products
from prompts import product_list


# Load environment variables
load_dotenv()

# Shared LLM
haiku = model_haiku_3
sonnet = model_sonnet_37

def analyzer(name:str):

    analyzer_agent = create_react_agent(
        model=haiku,
        tools=[get_customer_info],
        prompt="You are a expert financial helper, analyze the user data obtained from his bank statements. Create a Brief Report that guesses in 400 words what is the user financial situation, if it is healthy, what are the main components of his spending habits and how can he improve his situation." 
    )

    prompt_proposal = """You are a expert financial seller, MAKE A COMMERCIAL OFFER FOR A CLIENT GIVEN THE AVAILABLE PRODUCT LIST AND THE PRODUCTS CURRENTLY USED:
    AVAILABLE PRODUCT LIST
    - Auto loan: [Optimal Refinance Auto Loan, Prime Lease Buyout, Elite Lease Buyout, Select Used Car Loan, Value Auto Loan, Advanced Electric Vehicle Loan, Exclusive Used Car Loan, Prestige Refinance Auto Loan, Premium Refinance Auto Loan, Standard Lease Buyout]  
    - Checking Account: [Ultimate Student Checking, Preferred Interest Checking, Premium Basic Checking, Deluxe Basic Checking, Exclusive Business Checking, Classic Checking, Basic Student Checking, Standard Basic Checking, Premium Student Checking, Deluxe Interest Checking]  
    - Credit card: [Preferred Cash Back Card, Platinum Student Card, Optimal Student Card, Value Secured Card, Standard Student Card, Select Student Card, Classic Student Card, Smart Platinum Card, Prime Rewards Card, Prime Student Card, Premier Cash Back Card, Elite Cash Back Card, Gold Rewards Card, Premier Cash Back Card, Flex Rewards Card, Advanced Travel Card, Prime Rewards Card, Classic Business Card, Freedom Cash Back Card, Exclusive Secured Card]  
    - Insurance: [Smart Auto Insurance, Signature Home Insurance, Premium Home Insurance, Preferred Life Insurance, Prestige Home Insurance, Exclusive Life Insurance, Classic Life Insurance, Exclusive Renters Insurance, Elite Home Insurance, Prime Home Insurance]  
    - Investment: [Premier ETF, Preferred Retirement Fund, Signature Mutual Fund, Elite ETF, Standard Retirement Fund, Basic Bond Fund, Platinum Retirement Fund, Standard Target Date Fund, Signature Index Fund, Platinum Mutual Fund]  
    - Mortgage: [Deluxe FHA Loan, Signature VA Loan, Classic Jumbo Mortgage, Flex Fixed-Rate Mortgage, Value FHA Loan, Elite Adjustable-Rate Mortgage, Premier Fixed-Rate Mortgage, Select FHA Loan, Platinum Jumbo Mortgage, Ultimate Fixed-Rate Mortgage]  
    - Personal loan: [Basic Wedding Loan, Gold Wedding Loan, Elite Debt Consolidation Loan, Freedom Home Improvement Loan, Ultimate Personal Loan, Standard Vacation Loan, Prestige Wedding Loan, Signature Personal Loan, Advantage Debt Consolidation Loan, Smart Debt Consolidation Loan, Basic Vacation Loan, Prime Emergency Loan, Platinum Wedding Loan, Flex Vacation Loan, Flex Home Improvement Loan]  
    - Savings Account: [Prime Savings, Exclusive Money Market, Premium Goal Savings, Deluxe Money Market, Advanced Kids Savings, Silver IRA, Premier Goal Savings, Gold Goal Savings, Value Savings, Optimal High-Yield Savings, Value Certificate of Deposit, Preferred Savings, Advanced Kids Savings, Advanced High-Yield Savings, Standard Kids Savings]
    \n
    PRODUCTS CURRENTLY USED: AVAILABLE USING THE TOOL get_customer_info
    make an offer, showing the products offered and why this offering helps his concrete situation. PLEASE MAKE THE COMMERCIAL OFFER"""



    proposal_agent = create_react_agent(
        model=sonnet,
        tools=[get_customer_current_products],
        prompt=prompt_proposal
    )

    # Define LangGraph state
    class AgentState(TypedDict):
        messages: List

    # Wrap each agent in a node function
    def run_analyzer_agent(state: AgentState) -> AgentState:
        result = analyzer_agent.invoke(state)
        return {"messages": result["messages"]}

    def run_proposal_agent(state: AgentState) -> AgentState:
        result = proposal_agent.invoke(state)
        return {"messages": result["messages"]}

    # def run_travel_agent(state: AgentState) -> AgentState:
    #     result = travel_agent.invoke(state)
    #     return {"messages": result["messages"]}

    # def run_planner_agent(state: AgentState) -> AgentState:
    #     result = planner_agent.invoke(state)
    #     return {"messages": result["messages"]}

    # Build the graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("analyzer_agent", run_analyzer_agent)
    graph.add_node("proposal_agent", run_proposal_agent)

    # Connect nodes
    graph.add_edge(START, "analyzer_agent")
    graph.add_edge("analyzer_agent", "proposal_agent")
    graph.add_edge("proposal_agent", END)

    # Compile
    app = graph.compile()

    # Run the graph
    initial_input = {"messages": [HumanMessage(content=f"Analyze user history of {name}")]}
    result = app.invoke(initial_input)

    return result



# print(f"messages: {result["messages"]}")
# print(f"analisis: {result["financial_analysis"]}")
# print(f"offering: {result["sales_offering"]}")