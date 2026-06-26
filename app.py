<<<<<<< HEAD
﻿from flask import Flask, render_template, request, jsonify
import requests, json

app = Flask(__name__)
API_KEY = open("secret.txt").read().strip()

PROMPT = """You are a UAE business advisor for Al Ain and Al Qua'a. Return ONLY valid JSON:
{"business_name_suggestion":"string","summary":"string","steps":[{"step_number":1,"action":"string","description":"string","estimated_cost_aed":500,"timeline_days":7,"who_to_contact":"string","location":"string"}],"total_estimated_cost_aed":5000,"total_timeline_days":60,"first_customer_tip":"string"}
Exactly 5 steps. Costs in AED. UAE context: ADDED, Khalifa Fund, DED Al Ain."""

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    full_prompt = f"{PROMPT}\n\nBusiness idea: {data['idea']}\nCategory: {data['category']}\nBudget: {data['budget']} AED\nLocation: Al Qua'a / Al Ain, UAE"
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": f"Business idea: {data['idea']}\nCategory: {data['category']}\nBudget: {data['budget']} AED\nLocation: Al Qua'a / Al Ain, UAE"}
            ],
            "temperature": 0.7,
            "response_format": {"type": "json_object"}
        }
    )
    result = resp.json()
    print(result)
    text = result["choices"][0]["message"]["content"]
    return jsonify(json.loads(text))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
=======

>>>>>>> d081b13b5bad34ddff0387ae94324b5a5c2e1773
