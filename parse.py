
import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import logging

# Load the Groq API key from the environment variable
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key is None:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

# Initialize the LLM model using ChatGroq with the API key
llm = ChatGroq(
    model="llama-3.2-1b-preview",
    api_key=groq_api_key,
    timeout=300,
)

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

def parse_with_groq(dom_chunks, parse_description):
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm 

    parsed_results = []

    for i, chunk in enumerate(dom_chunks, start=1):
        # Add print statements here
        print(f"Parsing chunk: {chunk}")
        print(f"Parse description: {parse_description}")
        print(f"DOM Chunks: {dom_chunks}")


        try:
            response = chain.invoke({"dom_content": chunk, "parse_description": parse_description})
            print(f"Response content: {response.content}")
            parsed_results.append(response.content)
        except Exception as e:
            logging.error(f"Error parsing batch {i}: {e}")
            parsed_results.append(f"Error: {e}")


    return "\n".join(parsed_results)

