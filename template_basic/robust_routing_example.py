"""
Example: More robust routing using structured output with Pydantic
"""
from typing import Literal
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class RouteDecision(BaseModel):
    """Structured output for routing decision"""
    route: Literal["faq", "rag", "llm"] = Field(
        description="The knowledge source to use for answering"
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Confidence in the routing decision (0-1)"
    )
    reasoning: str = Field(
        description="Brief explanation for the routing choice"
    )

def create_robust_router(llm: ChatOpenAI):
    """Create a structured output router"""
    
    prompt = ChatPromptTemplate.from_template("""
    You are a smart routing agent. Analyze the user question and decide which source to use.
    
    Sources:
    - FAQ: Basic company info (HQ, CEO, founding, products) for Apple, Google, Intel, Tesla, Amazon
    - RAG: Detailed 2024 annual report data for these companies
    - LLM: General knowledge, creative tasks, unrelated questions
    
    Question: {question}
    Context: {context}
    
    Consider:
    - Question specificity and detail level required
    - Whether it relates to the supported companies
    - Type of information needed (basic vs detailed financial)
    """)
    
    # Use structured output - no string parsing needed!
    structured_llm = llm.with_structured_output(RouteDecision)
    return prompt | structured_llm

# Usage example:
async def route_with_structure(question: str, context: str = "") -> RouteDecision:
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    router = create_robust_router(llm)
    
    decision = await router.ainvoke({
        "question": question,
        "context": context
    })
    
    print(f"Route: {decision.route}")
    print(f"Confidence: {decision.confidence}")
    print(f"Reasoning: {decision.reasoning}")
    
    return decision
