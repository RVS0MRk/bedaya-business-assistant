import requests, json

with open("app.py") as f:
    content = f.read()
key = content.split('API_KEY = "')[1].split('"')[0]
print("Key starts with:", key[:10])

resp = requests.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
    headers={"x-goog-api-key": key, "Content-Type": "application/json"},
    json={
        "contents": [{"parts": [{"text": "Return this exact JSON: {\"message\":\"hello\"}"}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
)
print("Status:", resp.status_code)
print("Response:", json.dumps(resp.json(), indent=2))
