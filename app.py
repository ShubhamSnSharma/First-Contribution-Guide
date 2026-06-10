from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
from groq import Groq
import markdown


load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    issue_url = ""

    if request.method == "POST":
        issue_url = request.form.get("issue_url")
        try:
            parts = issue_url.replace("https://github.com/", "").split("/")
            owner = parts[0]
            repo = parts[1]
            issue_number = parts[3]

            api_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
            response = requests.get(api_url)
            data = response.json()

            if "message" in data:
                error = "Issue not found. Please check the URL."
            else:
                title = data["title"]
                body = data["body"]
                labels = [label["name"] for label in data["labels"]]

                prompt = f"""You are helping a beginner developer contribute to open source for the very first time. They have never made a pull request before and may not know basic Git commands.

Given this GitHub issue:

Title: {title}
Labels: {labels}
Description: {body}

Give them:
1. What the issue is asking for in simple terms
2. What kind of code change would fix it
3. What skills they need
4. Difficulty for a beginner (easy/medium/hard) and why
5. Exactly what to comment on the issue to get assigned to it — give them the exact words to copy paste
6. What to do step by step after getting assigned. Write this like the person has never used Git before. Explain every command, what it does, and why they're running it. Don't assume they know anything. Be specific about where to click on GitHub and what to type in the terminal.
"""

                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                )
                result = markdown.markdown(chat_completion.choices[0].message.content)

        except Exception as e:
            error = f"Something went wrong: {str(e)}"

    return render_template("index.html", result=result, error=error, issue_url=issue_url)

if __name__ == "__main__":
    app.run(debug=True)