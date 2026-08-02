import os
import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

API_HOST = "v3.football.api-sports.io"
API_KEY = "e198108f6c6ecefca2c863b2ec752ec0"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/proxy', methods=['GET'])
def proxy():
    endpoint = request.args.get('endpoint')
    if not endpoint:
        return jsonify({"error": "Missing endpoint parameter"}), 400

    query_params = request.args.to_dict()
    query_params.pop('endpoint', None)
    
    # Correct headers for direct API-Sports v3 or RapidAPI
    headers = {
        "x-apisports-key": API_KEY,
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": API_HOST
    }

    try:
        response = requests.get(f"https://{API_HOST}/{endpoint}", headers=headers, params=query_params, timeout=10)
        data = response.json()
        print(f"API Response for {endpoint}:", data)
        return jsonify(data)
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return jsonify({"error": str(e), "response": []}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)