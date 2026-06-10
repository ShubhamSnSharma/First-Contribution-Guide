import requests 
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-lite")

issue_url = input("Paste the GitHub issue URL: ")

parts = issue_url.replace("https://github.com/", "").split("/")

owner = parts[0]
repo = parts[1]
issue_number = parts[3]

url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"

response = requests.get(url)

data = response.json()

if "message" in data:
    print(data["message"])
    print("Try another issue number")
else:
    title = data["title"]
    body = data["body"]
    labels = [label["name"] for label in data["labels"]]

    print("Fetched issue. Asking Gemini to explain it...")
    print("------------------")

    prompt = f"""You are helping a beginner developer contribute to open source for the first time.

    Given this GitHub issue:

    Title: {title}
    Labels: {labels}
    Description: {body}

    Give them:
    1. What the issue is asking for in simple terms
    2. What kind of code change would fix it
    3. What skills they need
    4. Difficulty for a beginner (easy/medium/hard) and why
    5. Exactly what to comment on the issue to get assigned to it
    6. What to do step by step after getting assigned — fork, clone, find the right files, make the change, open a PR
    """

    result = model.generate_content(prompt)
    print(result.text)