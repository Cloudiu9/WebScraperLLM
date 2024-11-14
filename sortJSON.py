import json
from datetime import datetime
import re

def extract_date(content):
    # Use regex to find the publication date pattern (e.g., "October 13, 2023, 11:15")
    date_match = re.search(r"Publication date:(.*)", content)
    if date_match:
        # Convert to datetime for sorting
        date_str = date_match.group(1).strip()
        return datetime.strptime(date_str, "%B %d, %Y, %H:%M")
    return datetime.min  # Fallback if no date found

# Load the JSON data
with open("scraped_content.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# Sort data by the extracted publication date
data.sort(key=lambda x: extract_date(x['content']), reverse=True)

# Save the sorted data to a new JSON file
with open("sorted_transcripts.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)
