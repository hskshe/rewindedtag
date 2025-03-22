from flask import Flask, request, jsonify
import requests
import json
import hashlib
import os
from datetime import datetime

app = Flask(__name__)

WEBHOOK_URL = os.getenv("https://discord.com/api/webhooks/1353093075194351677/NSkTvNOv-FANbHg0J4YvfIqX4S-RQfrhofZ4H9dlu12DDbmReTt_4G_mLWgmsTZMcQmu")
WEBHOOK_URL_2 = os.getenv("https://discord.com/api/webhooks/1353093328174055506/aXlCwNQ43qOhxw2T913zBv1w9gEHztYH69BN3F_PqMzuS6tKXYtA5el0vbzMFwPVqCNQ")

title_data = {}

def load_title_data_from_file():
    try:
        with open('title_data.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("title_data.json not found. Starting with an empty dictionary.")
        return {}
    except Exception as e:
        print(f"Error loading title data: {e}")
        return {}

def save_title_data_to_file(data):
    try:
        with open('title_data.json', 'w') as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        print(f"Error saving title data: {e}")

def hash_md5(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

@app.route('/', methods=['GET'])
def get_title_data():
    print('Title data fetched:', title_data)
    return jsonify(title_data), 200

@app.route('/', methods=['POST'])
def update_title_data():
    global title_data
    received_data = request.json.get('data', {})
    title_data = received_data
    save_title_data_to_file(title_data)
    return jsonify({"message": "Data updated successfully"}), 200

@app.route('/api/photon', methods=['POST'])
def photon_api():
    data = request.json
    user_id = data.get("UserId")
    nonce = data.get("Nonce")
    data["timestamp"] = datetime.utcnow().isoformat()
    print(data)
    send_to_discord_webhook(data)
    send_to_discord_webhook2(nonce)
    return jsonify({
        "ResultCode": 1,
        "UserId": user_id
    }), 200

@app.route('/api/playfabauthenticate', methods=['POST'])
def playfab_auth():
    data = request.json
    send_to_discord_webhook(data)
    user_id = data.get('UserId')
    platform = data.get('Platform')
    if user_id and platform:
        return jsonify({
            "ResultCode": 1,
            "UserId": user_id,
            "Platform": platform
        }), 200
    else:
        ban_info = {
            "BanReason": "You made a mistake",
            "BanDuration": "72 hours",
            "Timestamp": datetime.utcnow().isoformat()
        }
        return jsonify({"Error": "Forbidden", "Message": "Invalid data received", "BanInfo": ban_info}), 403

@app.route('/api/cacheplayfabid', methods=['POST'])
def cache_playfab_id():
    data = request.json
    send_to_discord_webhook(data)
    required_fields = ['Platform', 'SessionTicket', 'PlayFabId']
    if all(field in data for field in required_fields):
        return jsonify({"Message": "PlayFabId Cached Successfully"}), 200
    else:
        missing_fields = [field for field in required_fields if field not in data]
        return jsonify({"Error": "Missing Data", "MissingFields": missing_fields}), 400

def send_to_discord_webhook(log_data):
    if WEBHOOK_URL:
        content = f"Auth Post Data:\n```json\n{json.dumps(log_data, indent=2)}\n```"
        requests.post(WEBHOOK_URL, json={"content": content})
    else:
        print("Discord webhook URL not set.")

def send_to_discord_webhook2(nonce):
    if WEBHOOK_URL_2:
        content = f"Nonce is:\n```json\n{json.dumps(nonce, indent=2)}\n```"
        requests.post(WEBHOOK_URL_2, json={"content": content})
    else:
        print("Second Discord webhook URL not set.")

if __name__ == '__main__':
    title_data = load_title_data_from_file()
    app.run(host='0.0.0.0', port=8080)
