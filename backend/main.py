from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import json

app = FastAPI()

MISTRAL_API_KEY = "LDIPhUAb8kUwgmwzX88ADpT2tBXj8UY0"
MISTRAL_API_URL = "https://api.mistral.ai/v1/completions"

# Define request model
class ModifyRequest(BaseModel):
    request: str
    html: str

# Function to query Mistral CodeGen API
def generate_js_modifications(user_request, page_html):
    prompt = f"""
    The user wants to modify the website. Their request: "{user_request}"
    Given this HTML: {page_html}
    Generate a JavaScript function that makes the requested modifications.
    Return only valid JavaScript inside a function called applyModifications().
    Example:
    function applyModifications() {{
        document.querySelectorAll('p').forEach(el => el.style.fontSize = '22px');
    }}
    """

    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "mistral-codegen",  # Use the CodeGen model
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 200
    }

    response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        generated_code = response.json()["choices"][0]["message"]["content"]
        return generated_code.strip()
    else:
        return "function applyModifications() { console.error('Error generating code'); }"

# Process user modification requests
@app.post("/modify")
async def modify_page(data: ModifyRequest):
    user_request = data.request
    page_html = data.html

    generated_js = generate_js_modifications(user_request, page_html)

    return {"javascript": generated_js}
