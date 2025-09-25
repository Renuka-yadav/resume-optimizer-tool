import os
import requests
from dotenv import load_dotenv

# --- Configuration ---
MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

# --- 1. Load Environment Variables ---
print("--- Step 1: Loading environment variables ---")
load_dotenv()
hf_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# --- 2. Check if the Token was Loaded ---
print("\n--- Step 2: Checking the API Token ---")
if not hf_token:
    print("RESULT: FAILURE! The Hugging Face token was not found.")
    print("Please ensure your .env file is in the 'backend' folder and contains the correct key.")
else:
    print(f"RESULT: SUCCESS! Token loaded. It starts with: {hf_token[:7]}...") # Shows only the first few chars for security

# --- 3. Attempt to Call the API ---
print("\n--- Step 3: Calling the Hugging Face API ---")
if hf_token:
    headers = {"Authorization": f"Bearer {hf_token}"}
    payload = {
        "inputs": "Can you please answer this question?",
        "parameters": {"max_new_tokens": 50}
    }

    try:
        response = requests.post(MODEL_URL, headers=headers, json=payload, timeout=20)

        print(f"API Response Status Code: {response.status_code}")
        print("API Response Text:")
        print(response.text)

        if response.status_code == 200:
            print("\nRESULT: SUCCESS! The API call worked correctly.")
        else:
            print(f"\nRESULT: FAILURE! The API returned an error (Code: {response.status_code}).")
            if response.status_code == 404:
                 print("This '404 Not Found' error likely points to a network issue (firewall/proxy) or an invalid API key.")

    except requests.exceptions.RequestException as e:
        print("\nRESULT: CRITICAL FAILURE! Could not connect to the Hugging Face server.")
        print(f"Error details: {e}")
        print("This strongly suggests a network issue is blocking the connection.")