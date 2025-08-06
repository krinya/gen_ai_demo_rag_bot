"""
Example: Function calling approach for routing
"""
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

@tool
def route_to_faq(question: str) -> str:
    """Use FAQ source for basic company information like CEO, headquarters, founding year, notable products."""
    return f"Routing to FAQ for: {question}"

@tool  
def route_to_rag(question: str) -> str:
    """Use RAG source for detailed 2024 annual report information about financials, metrics, specific data."""
    return f"Routing to RAG for: {question}"

@tool
def route_to_llm(question: str) -> str:
    """Use LLM for general knowledge, creative tasks, or questions unrelated to supported companies."""
    return f"Routing to LLM for: {question}"

def create_function_calling_router(llm: ChatOpenAI):
    """Create a function-calling based router"""
    
    tools = [route_to_faq, route_to_rag, route_to_llm]
    llm_with_tools = llm.bind_tools(tools)
    
    prompt = ChatPromptTemplate.from_template("""
    You are a routing agent. Based on the question, call the appropriate routing function.
    
    Question: {question}
    Context: {context}
    
    Choose the best source and call the corresponding function.
    """)
    
    return prompt | llm_with_tools

# Usage:
async def route_with_functions(question: str, context: str = ""):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    router = create_function_calling_router(llm)
    
    result = await router.ainvoke({
        "question": question,
        "context": context
    })
    
    # Extract the function call
    if result.tool_calls:
        tool_call = result.tool_calls[0]
        function_name = tool_call["name"]
        route = function_name.replace("route_to_", "")
        print(f"Selected route: {route}")
        return route
    
    return "llm"  # fallback
