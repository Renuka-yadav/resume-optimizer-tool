import requests
from bs4 import BeautifulSoup

def extract_linkedin_info(profile_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(profile_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Try to extract experience/skills sections
    text = soup.get_text(separator=' ')
    return text[:2000]  # Trim to avoid overload
