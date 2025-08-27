from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])  # <- match your React origin

@app.route("/api/get_clothing", methods=["POST"])
def get_clothing():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
    

    temp = data.get("temp")
    feelslike = data.get("feelslike")
    rain = data.get("precip")
    humidity = data.get("humidity")
    windspeed = data.get("windspeed")
    uvindex = data.get("uvindex")

    prompt = f"""
    Recommend gender-neutral clothing based on the following weather:
    - Temperature: {temp}°F
    - Feels like: {feelslike}°F
    - Rain: {rain}%
    - Humidity: {humidity}%
    - Windspeed: {windspeed} mph
    - UV Index: {uvindex}
    Make it concise and practical keep it under 80 words.
    """
    try:
        response = openai.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return jsonify({"rewritten": response.output_text})
    except Exception as e:
        print(e)
        return jsonify({"error": "OpenAI request failed"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)