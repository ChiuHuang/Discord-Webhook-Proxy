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
    r1 = data.get("r1", 0)
    r2 = data.get("r2", 0)
    is_low = (p <= 10 and not chg)
    content = f"<@{user_id}>  Your Battery Is Dying..." if is_low else ""
    """
    
R1: ON, R2: ON -> NO POWER
R1: ON, R2: OFF -> BAT ONLY 
R1: OFF, R2: OFF -> BAT+WALL 
R1: OFF, R2: ON -> WALL POWER 

peak soldering skills ahh 

"""
    color = 0xFF0000 if is_low else (0x00FF00 if chg else 0xFFFF00)
    status_text = "Charging" if chg else "Battery Mode"
    possibleMode = {
        
        (1, 1): "NOPOWER",
        (1, 0): "BAT ONLY",
        (0, 0): "BAT+WALL",
        (0, 1): "WALL ONLY"
    }.get((r1, r2), "UNKNOWN")
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
                },
                
                {
                    "name": "Possable Mode",
                    "value": f"Mode: {possibleMode} Relay1:{r1},Relay2:{r2}"
                },
                
            ],
            "timestamp": None
        }]
    }

    resp = requests.post(url, json=payload)
    return jsonify({"discord_code": resp.status_code}), resp.status_code

if __name__ == '__main__':
    app.run(debug=True)
