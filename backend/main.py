from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import json
import iris  # InterSystems IRIS Python API

app = FastAPI()

MISTRAL_API_KEY = "LDIPhUAb8kUwgmwzX88ADpT2tBXj8UY0"
MISTRAL_API_URL = "https://api.mistral.ai/v1/completions"

# Connect to InterSystems IRIS
IRIS_CONNECTION = iris.connect(
    "localhost", 1972, "USER", "_SYSTEM", "SYS"
)

# Define request model
class ModifyRequest(BaseModel):
    request: str
    html: str
    url: str  # Include the site URL for preference storage

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
        "model": "mistral-codegen",
        "messages": [{"role": "system", "content": prompt}],
        "max_tokens": 200
    }

    response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        generated_code = response.json()["choices"][0]["message"]["content"]
        return generated_code.strip()
    else:
        return "function applyModifications() { console.error('Error generating code'); }"

# Store user preferences in InterSystems IRIS
def save_user_preference(url, user_request, js_code):
    query = "INSERT INTO UserPreferences (url, request, js_code) VALUES (?, ?, ?)"
    with IRIS_CONNECTION.cursor() as cur:
        cur.execute(query, (url, user_request, js_code))
    IRIS_CONNECTION.commit()

# Retrieve stored preferences for a site
def get_user_preferences(url):
    query = "SELECT js_code FROM UserPreferences WHERE url = ?"
    with IRIS_CONNECTION.cursor() as cur:
        cur.execute(query, (url,))
        return [row[0] for row in cur.fetchall()]

# Process user modification requests
@app.post("/modify")
async def modify_page(data: ModifyRequest):
    user_request = data.request
    page_html = data.html
    url = data.url

    generated_js = generate_js_modifications(user_request, page_html)
    save_user_preference(url, user_request, generated_js)

    return {"javascript": generated_js}

# Retrieve stored preferences for a given site
@app.get("/preferences")
async def get_preferences(url: str):
    stored_js = get_user_preferences(url)
    return {"javascript": stored_js}
