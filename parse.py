import os
from groq import Groq
import logging

logging.basicConfig(level=logging.INFO)

# Load the Groq API key from the environment variable
groq_api_key = os.getenv("GROQ_API_KEY")
if groq_api_key is None:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

# Initialize the Groq client
client = Groq(api_key=groq_api_key)

def parse_with_groq(dom_chunks, parse_description):
    parsed_results = []
    logging.info("Starting parsing with Groq...")

    for chunk in dom_chunks:
        logging.info(f"Processing chunk: {chunk}")  # Log the current chunk being processed
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are tasked with analyzing speech transcripts."},
                    {"role": "user", "content": f"Analyze the following speech text and extract:\n"
                                                 f"- Date of the speech\n"
                                                 f"- Location\n"
                                                 f"- Main topics discussed\n"
                                                 f"- Key quotes\n\n"
                                                 f"Text: {chunk}"}
                ],
                model="llama3-8b-8192"
            )
            logging.info(f"Response received: {response}")  # Log the API response
            
            if response.choices:  # Check if choices is not empty
                parsed_results.append(response.choices[0].message.content)
            else:
                logging.warning("No choices returned in the API response.")  # Log a warning if no choices are available
            
        except Exception as e:
            logging.error(f"Error: {e}")  # General error logging

    return "\n".join(parsed_results)

