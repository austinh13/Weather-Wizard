from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import openai
from dotenv import load_dotenv
import sqlite3

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)

"""Initializes the SQLite database and creates the ClothingRecs table."""
def init_db():
    conn = sqlite3.connect("suggestions.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ClothingRecs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temp REAL,
            feelslike REAL,
            rain REAL,
            humidity REAL,
            windspeed REAL,
            uvindex REAL,
            recommendation TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

"""Fetches a GPT recommendation from the database"""
def get_recommendation(temp, feelslike, rain, humidity, windspeed, uvindex):
    conn = sqlite3.connect("suggestions.db")
    # FIX: Corrected missing parentheses to get a cursor object
    c = conn.cursor()
    c.execute("""
        SELECT recommendation FROM ClothingRecs
        WHERE temp=? AND feelslike=? AND rain=? AND humidity=? AND windspeed=? AND uvindex=?
    """, (temp, feelslike, rain, humidity, windspeed, uvindex))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

"""Saves GPT recommendation to the database."""
def save_recommendation(temp, feelslike, rain, humidity, windspeed, uvindex, recommendation):
    # FIX: Corrected database filename to be consistent ("suggestions.db")
    conn = sqlite3.connect("suggestions.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO ClothingRecs (temp, feelslike, rain, humidity, windspeed, uvindex, recommendation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (temp, feelslike, rain, humidity, windspeed, uvindex, recommendation))
    conn.commit()
    conn.close()

@app.route("/api/get_clothing", methods=["POST"])
def get_clothing():

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400
    
    # FIX: Moved variable assignments to the top of the function
    # This ensures the variables are defined before they are used.
    temp = data.get("temp")
    feelslike = data.get("feelslike")
    rain = data.get("precip")
    humidity = data.get("humidity")
    windspeed = data.get("windspeed")
    uvindex = data.get("uvindex")

    if any(p is None for p in [temp, feelslike, rain, humidity, windspeed, uvindex]):
        return jsonify({"error": "Missing required weather parameters"}), 400

    existing = get_recommendation(temp, feelslike, rain, humidity, windspeed, uvindex)
    if existing:
        return jsonify({"recommendation": existing, "cached": True})
    
    prompt = f"""
    Recommend gender-neutral clothing based on the following weather:
    - Temperature: {temp}°F
    - Feels like: {feelslike}°F
    - Rain: {rain}%
    - Humidity: {humidity}%
    - Windspeed: {windspeed} mph
    - UV Index: {uvindex}
    Make it concise and practical. Keep it under 80 words.
    """
    try:

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # FIX: Correctly access the generated text from the API response
        rec = response.choices[0].message.content

        # Save new recommendation
        save_recommendation(temp, feelslike, rain, humidity, windspeed, uvindex, rec)
        return jsonify({"recommendation": rec, "cached": False})
    except Exception as e:
        print(f"An error occurred with the OpenAI request: {e}")
        return jsonify({"error": "OpenAI request failed"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
