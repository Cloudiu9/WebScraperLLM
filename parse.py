# Import necessary components for integrating the Ollama LLM with Python
from langchain_ollama import OllamaLLM  # Connects Large Language Models (LLMs) to Python
from langchain_core.prompts import ChatPromptTemplate  # For creating prompts for the LLM

# Define a template for the LLM, providing instructions on how to extract information from the DOM content
template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

# Initialize the LLM model using Ollama; specifying a model version, depending on the one installed from https://github.com/ollama/ollama
# Ex: ollama run llama3.2 OR ollama run llama3.2:1b
model = OllamaLLM(model="llama3.2:1b")

# Function that interacts with the LLM to parse the DOM content in chunks based on the provided description
def parse_with_ollama(dom_chunks, parse_description):
    # Create a prompt using the defined template, which combines the DOM content and description
    prompt = ChatPromptTemplate.from_template(template)

    # Create a processing chain: input (prompt) --> process (model)
    chain = prompt | model 

    # Initialize a list to store parsed results from each chunk
    parsed_results = []

    # Loop through each chunk of the DOM content and send it to the LLM for processing
    for i, chunk in enumerate(dom_chunks, start=1):
        # Call the LLM with the current chunk and the parsing instructions
        response = chain.invoke({"dom_content": chunk, "parse_description": parse_description})

        # Log progress by showing which chunk is being processed
        print(f"Parsed batch {i} of {len(dom_chunks)}")

        # Append the LLM's response to the parsed_results list
        parsed_results.append(response)

    # Join the parsed results from all chunks into a single string and return it
    return "\n".join(parsed_results)
