from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)


@app.route('/ups-ping', methods=['POST'])
def ups_ping():
    data = request.json
    if not data:
        return jsonify({"error": "No data"}), 400
    url = data.get("url", "")
    v = data.get("v", 0.0)    # volt
    p = data.get("p", 0)      # percent
    chg = data.get("chg", False) # Charging
    user_id = data.get("id", "") # Discord ID

    is_low = (p <= 10 and not chg)
    content = f"<@{user_id}>  Your Battery Is Dying..." if is_low else ""
    
    color = 0xFF0000 if is_low else (0x00FF00 if chg else 0xFFFF00)
    status_text = "Charging" if chg else "Battery Mode"

    # Construct the Discord Payload
    payload = {
        "content": content,
        "embeds": [{
            "title": "UPS System Status",
            "color": color,
            "description": f"**Voltage:** `{v}V`\n**Battery:** `{p}%`\n**Status:** {status_text}",
            "fields": [
                {
                    "name": "Power Level",
                    "value": f"`{'█' * (p // 10)}{'░' * (10 - (p // 10))}` {p}%"
                }
            ],
            "footer": {"text": "ESP32-P4 N16R8 Monitor :3"},
            "timestamp": None
        }]
    }

    resp = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    return jsonify({"discord_code": resp.status_code}), resp.status_code

if __name__ == '__main__':
    app.run(debug=True)
