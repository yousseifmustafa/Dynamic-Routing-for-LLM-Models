import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface.chat_models import ChatHuggingFace

load_dotenv()


if not os.getenv("HF_API_KEY"):
    raise ValueError("Cant Find Your Hugging Face Token")
else:
    api_key = os.getenv("HF_API_KEY")


query_cache = {}



simple_llm = ChatHuggingFace(llm=HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.2-3B-Instruct",
    huggingfacehub_api_token=api_key,
    temperature=0.2,
    max_new_tokens=100,
    timeout=60
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
    ("ai", "Advanced"),

    ("human", "Query: '{query}'")
])


simple_template = ChatPromptTemplate.from_messages([
    ("system", "You are a straightforward, factual assistant. Answer the user's question very concisely and directly in one or two sentences."),
    ("human", "{query}")
])


medium_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful and clear assistant. Fulfill the user's request thoroughly."),
    ("human", "{query}")
])

advanced_template = ChatPromptTemplate.from_messages([
    ("system", "You are a world-class strategic analyst and problem-solver. Your task is to analyze and provide a comprehensive, step-by-step solution for the following complex request. Let's think step-by-step before providing the final answer."),
    ("human", "{query}")
])

simple_chain = simple_template | simple_llm
medium_chain = medium_template | medium_llm
advanced_chain = advanced_template | advanced_llm
classification_chain = router_template | simple_llm


def call_model(chain, query: str, model_name: str):
    try:
        response = chain.invoke({"query": query})
        return response.content, None  
    except Exception as e:
        error_msg = f"Error from {model_name} Model: {e}\n"
        print(error_msg, end="")
        return None, error_msg 
    

def classify_query(query: str) -> str:
    try:
        response = classification_chain.invoke({"query": query}) 
        result = response.content.strip()
        if result in ["Simple", "Medium", "Advanced"]:
            return result
        else:
            return "Medium"
    except Exception  :
            return "Medium"
            


def route_query(query: str):
    if query in query_cache:
        return query_cache[query], ""

    classification = classify_query(query)
    print(f"Query classified as: {classification}")
    
    answer = None
    logs = ""
    
    if classification == "Simple":
        models_to_try = [("Simple", simple_chain), ("Medium", medium_chain), ("Advanced", advanced_chain)]
    elif classification == "Medium":
        models_to_try = [("Medium", medium_chain), ("Advanced", advanced_chain), ("Simple", simple_chain)]
    else: 
        models_to_try = [("Advanced", advanced_chain), ("Medium", medium_chain), ("Simple", simple_chain)]


    for name, chain in models_to_try:
        answer, error = call_model(chain, query, name)
        if error:
            logs += error
        if answer:
            print(f"Success with {name} model!")
            break 
        
    if not answer:
        answer = "Sorry, all models failed to respond."

    query_cache[query] = answer
    return answer, logs


def write_to_file(filepath: str, content: str):
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Failed to write to {filepath}: {e}")


if __name__ == "__main__":
    test_queries = [
        "2+2",
        "Translate 'Good morning' to Arabic",
        "Hi , Ai" ,
        "What is AI?",
        "Write a short paragraph about sleep benefits",
        "Write an email requesting a leave",
        "Explain how a car engine works",
        "6-month marketing plan for a startup","Write an email requesting a leave",
        "Fix Java code with NullPointerException",
        "Summarize a story of The Tell-Tale Heart",
        "What is the core message in the following 30-word text about responsible AI: 'Developing artificial intelligence requires a deep commitment to fairness, transparency, and accountability to ensure technology serves all of humanity justly?",
        "Python code to print even numbers 1–10",
        "Solve 2x² + 3x - 5 = 0"
    ]

    all_answers_list = []
    all_logs_list = []
    i=1 
    for q in test_queries:
        print("\n"*3)
        final_answer, query_logs = route_query(q) 
        
        print("\n"*3)
        print(final_answer)
        print("\n"*3)
        
        all_answers_list.append(f"Q {i}: {q}\n A {i}: {final_answer}\n" + "\n"*3)
        if query_logs:
            all_logs_list.append(f"Logs for query '{q}':\n{query_logs}")
        i+=1
            
    write_to_file("Answers.txt", "\n".join(all_answers_list))
    write_to_file("logs.txt", "\n".join(all_logs_list))
