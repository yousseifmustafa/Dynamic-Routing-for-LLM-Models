import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface.chat_models import ChatHuggingFace

load_dotenv()

if not os.getenv("HF_API_KEY"):
    raise ValueError("Hugging Face API token not found. Please set it in your .env file.")
else:
    api_key = os.getenv("HF_API_KEY")


# Defining LLMs 
simple_llm = ChatHuggingFace(llm=HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.2-3B-Instruct",
    huggingfacehub_api_token=api_key,
    temperature=0.2
    ))

medium_llm = ChatHuggingFace(llm=HuggingFaceEndpoint(
    repo_id="meta-llama/Meta-Llama-3-8B-Instruct",
    huggingfacehub_api_token=api_key,
    temperature=0.5,
    max_new_tokens=500,
    timeout=120
))

advanced_llm = ChatHuggingFace(llm=HuggingFaceEndpoint(
    repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
    huggingfacehub_api_token=api_key,
    temperature=0.7,
    max_new_tokens=1024,
    timeout=180
))


router_template = ChatPromptTemplate.from_messages(
    [("system", """You are a precise and efficient Query Classifier. Your sole purpose is to analyze the user's query and classify it into one of three categories: 'Simple', 'Medium', or 'Advanced'.

Your response MUST be ONLY ONE WORD from that list. Do not add any explanation or conversation.

## Classification Criteria:

**1. Analyze the query based on these heuristic rules:**
    - **Word Count:** Less than 10 words leans 'Simple'. Less than 50 leans 'Medium'. More than 50 leans 'Advanced'.
    - **Keywords:** 'Analyze', 'plan', 'code' suggest 'Advanced'. 'Explain', 'summarize' suggest 'Medium'. 'What is', 'translate' suggest 'Simple'.

**2. Use your intelligent judgment as the final deciding factor:**
    - The rules above are just a guide. Your primary goal is to evaluate the *actual complexity and intent* of the query.
    - **Example of overriding rules:** The query "Solve a partial differential equation" is very short, but it is extremely 'Advanced'. Your judgment must override the word count rule here.

Return only one word: 'Simple', 'Medium', or 'Advanced'."""),
    ("human", "Query: 'Translate 'Good morning' to Arabic'"),
    ("ai", "Simple"),
    ("human", "Query: 'Create a 6-month marketing plan for a new startup'"),
    ("ai", "Advanced"),
    ("human", "Query: 'Solve 2x^2 + 3x - 5 = 0'"),
    ("ai", "Medium"),
    ("human", "Query: '{query}'")
])

# 2. Templates for each expert
simple_template = ChatPromptTemplate.from_messages([
    ("system", "You are a straightforward, factual assistant. Answer the user's question very concisely and directly in one or two sentences."),
    ("human", "{query}")
])

medium_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful and clear assistant. Fulfill the user's request thoroughly and provide a well-structured answer."),
    ("human", "{query}")
])

advanced_template = ChatPromptTemplate.from_messages([
    ("system", "You are a world-class strategic analyst and problem-solver. Your task is to analyze and provide a comprehensive, step-by-step solution for the following complex request. Let's think step-by-step before providing the final answer."),
    ("human", "{query}")
])


# A chain for each path the query can take
simple_chain = simple_template | simple_llm
medium_chain = medium_template | medium_llm
advanced_chain = advanced_template | advanced_llm
classification_chain = router_template | simple_llm # Use the fastest model for classification


def call_model(chain, query: str, model_name: str):
    """Invokes a given chain and handles potential exceptions, returning the response and logs."""
    try:
        response = chain.invoke({"query": query})
        return response.content, None  # (answer, error)
    except Exception as e:
        error_msg = f"Error from {model_name} Model: {e}\n"
        return None, error_msg # (answer, error)


def classify_query(query: str) -> str:
    """Classifies the query into 'Simple', 'Medium', or 'Advanced'."""
    try:
        response = classification_chain.invoke({"query": query})
        result = response.content.strip()
        if result in ["Simple", "Medium", "Advanced"]:
            return result
        else:
            # Default to Medium if classification is unclear
            return "Medium"
    except Exception:
        # Default to Medium on any classification error
        return "Medium"


def route_query(query: str, query_cache: dict):
    """
    The main function that classifies a query, routes it to the appropriate model,
    handles fallbacks, and uses a cache.
    """
    if query in query_cache:
        # If the answer is already in the cache, return it immediately
        return query_cache[query], "Fetched from cache."

    classification = classify_query(query)
    logs = f"Query classified as: {classification}\n"
    
    # Define the fallback chain based on the classification
    if classification == "Simple":
        models_to_try = [("Simple", simple_chain), ("Medium", medium_chain), ("Advanced", advanced_chain)]
    elif classification == "Medium":
        models_to_try = [("Medium", medium_chain), ("Advanced", advanced_chain), ("Simple", simple_chain)]
    else:  # Advanced
        models_to_try = [("Advanced", advanced_chain), ("Medium", medium_chain), ("Simple", simple_chain)]

    answer = None
    # Try the models in the defined order
    for name, chain in models_to_try:
        logs += f"Attempting to use {name} model...\n"
        answer, error = call_model(chain, query, name)
        if error:
            logs += error
        if answer:
            logs += f"Success with {name} model!\n"
            print(f"Success with {name} model!")
            break 
    
    if not answer:
        answer = "Sorry, all models failed to generate a response. Please try again later."
        logs += "All models failed.\n"

    # Save the final answer to the cache before returning
    query_cache[query] = answer
    return answer, logs
