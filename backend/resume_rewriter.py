import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

try:
    # Initialize the Groq client from the environment variable
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    client = None

class AIAuthError(Exception):
    """Custom exception for authentication or initialization errors."""
    pass

def rewrite_resume(resume_text, jd_text):
    """
    Rewrites a resume to be ATS-friendly and optimized for a specific job description using the Groq API.
    """
    if not client:
        raise AIAuthError("Groq client not initialized. Check your GROQ_API_KEY in the .env file.")

    # System prompt to define the AI's role and rules
    system_prompt = (
        "You are a professional resume writer. Your task is to optimize the provided resume for Data Analyst roles, making it ATS-friendly and industry-standard. "
        "Strictly follow these rules:\n"
        "1. Use plain structured text with clear section headers (Summary, Education, Technical Skills, Projects, Experience, Additional Information).\n"
        "2. Do not use any Markdown symbols like *, **, or -.\n"
        "3. Present information in bullet points where appropriate, using indentation.\n"
        "4. Integrate keywords like Python, SQL, Power BI, Tableau, Data Visualization, Data Analysis, and Business Intelligence.\n"
        "5. Rephrase project descriptions to an 'action-result' format, highlighting measurable outcomes (e.g., 'Increased accuracy by 30%').\n"
        "6. The tone must be professional, concise, and impact-driven.\n"
        "7. The final output must be only the clean, structured resume text, ready for a DOCX or PDF file."
    )

    # User prompt providing the specific resume and job description
    user_prompt = (
        f"Optimize the following resume based on the provided Job Description.\n\n"
        f"--- Original Resume ---\n{resume_text}\n\n"
        f"--- Job Description ---\n{jd_text}"
    )

    print("Sending resume and JD to Groq API for optimization...")

    try:
        # API call to the Groq service
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            model="llama-3.1-8b-instant",  # Using the latest supported model
            temperature=0.5,
            max_tokens=2048, # Increased token limit for longer resumes
        )
        
        # Extract the optimized resume from the API response
        response_text = chat_completion.choices[0].message.content
        print("Successfully received optimized resume from Groq.")
        return response_text.strip()

    except Exception as e:
        # Provide a clear error message if the API call fails
        print(f"An error occurred with the Groq API call: {e}")
        raise RuntimeError(f"Failed to get a response from the Groq API: {e}")