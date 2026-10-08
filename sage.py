import ollama
from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

SYSTEM_PROMPT = (
    "You are Sage, an AI assistant created by Theo Kershaw. "
    "You specialize in physics, astrology and astroengineering, etc. "
    "You will only respond with factual statements to answer a question even if it would hurt the users feelings."
)

history = []

def lm(query):
    try:
        response = ollama.chat(
            model='gemma3:4b',
            messages=[{'role': 'system', 'content': SYSTEM_PROMPT}] + history + [{'role': 'user', 'content': query}]
        )
        history.extend([
            {'role': 'user', 'content': query},
            {'role': 'assistant', 'content': response.message.content}
        ])
        return response.message.content
    except Exception as e:
        print(e)
        return e

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    query = request.get_data(as_text=True)
    response = lm(query)
    return response

if __name__ == "__main__":
    app.run(debug=True)