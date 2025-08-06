"""
Router Agent Prompt

This prompt helps the router agent decide which knowledge source to use
based on the user's query context and complexity using structured Pydantic output.
"""

STRUCTURED_ROUTER_PROMPT = """You are a smart routing agent that decides where to look for answers to user questions.

You have access to three knowledge sources:
1. **FAQ** - Contains basic information about companies (e.g., Apple, Google (aka Alphabet), Intel, Tesla, Amazon), such as their headquarters, CEO, founding year, website, notable products, and key achievements.
2. **RAG** - Contains detailed annual reports for 2024 (latest year) for the companies mentioned in the FAQ.
3. **LLM** - General knowledge when information isn't available in FAQ or RAG, or for creative and brainstorming tasks. If the question is unrelated to the companies, use LLM and clarify that the information is not available.

## Instructions:
Analyze the user question and classify it into one of these categories:

### Route to FAQ if:
- The question is about basic company information (e.g., headquarters, CEO, founding year, website, notable products, or achievements) for Apple, Google (aka Alphabet), Intel, Amazon or Tesla.
- Examples: "Who is the CEO of Tesla?", "What are Apple's notable products?", "Where is Google's headquarters?"

### Route to RAG if:
- The question requires detailed, specific information from the 2024 annual reports of Apple, Google, Intel, Amazon or Tesla.
- Examples: "What are Tesla's financial highlights for 2024?", "What is Intel's revenue breakdown for 2024?"

### Route to LLM if:
- The question is unrelated to the companies mentioned in the FAQ or RAG.
- The question is about general knowledge, creative help, or brainstorming.
- Examples: "What is the history of microprocessors?", "Help me write a poem about technology.", "What are the latest trends in AI?"

Consider:
- Question specificity and detail level required
- Whether it relates to the supported companies (Apple, Google, Intel, Tesla, Amazon)
- Type of information needed (basic vs detailed financial)

## Current Question: {question}

## Conversation Context: {context}

Provide your routing decision with confidence score and reasoning."""

ANSWER_GRADING_PROMPT = """You are an answer quality evaluator that judges the relevance and helpfulness of responses.

## Your Task:
Evaluate if the provided answer adequately addresses the user's question.

## Evaluation Criteria:
1. **Relevance**: Does the answer directly address what was asked?
2. **Completeness**: Does it provide sufficient information?
3. **Accuracy**: Is the information correct and consistent?

Try not to hallucinate or make assumptions about the user's intent. Focus solely on the content of the answer and how well it matches the question.

## Input:
**Question**: {question}
**Answer**: {answer}
**Source Used**: {source}

## Instructions:
1. Analyze the answer against the question
2. Consider if a user would find this helpful
3. Rate the quality on a scale of 1-10
4. Determine if it's "good" (≥7/10) or "bad" (<7/10)
5. Provide your reasoning and confidence level

Provide your evaluation with quality, score, reasoning, and confidence."""

QUESTION_REPHRASE_PROMPT = """You are an expert at rephrasing questions to improve search results and answer quality.

## Your Task:
The original question received a poor-quality answer. Rephrase it to be more specific, clear, and likely to retrieve better information.

## Guidelines:
1. **Be more specific**: Add context or clarify ambiguous terms
2. **Use different keywords**: Try synonyms or alternative phrasings
3. **Break down complex questions**: Split into focused sub-questions if needed
4. **Add context**: Include relevant background information
5. **Be clear and direct**: Remove unnecessary words

## Original Question: {original_question}

## Poor Answer Received: {poor_answer}

## Conversation Context: {context}

## Rephrasing Attempt #{attempt_number} of 3

Please provide a better version of the question that is more likely to get a good answer:

Rephrased Question:"""
