from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

COPYRIGHT_STRING = "@never_delete this source maker"

DESIRED_ORDER = [
    "Owner Name", "Father's Name", "Owner Serial No", "Model Name", "Maker Model",
    "Vehicle Class", "Fuel Type", "Fuel Norms", "Registration Date", "Insurance Company",
    "Insurance No", "Insurance Expiry", "Insurance Upto", "Fitness Upto", "Tax Upto",
    "PUC No", "PUC Upto", "Financier Name", "Registered RTO", "Address", "City Name", "Phone"
]

def get_vehicle_details(rc_number: str) -> dict:
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"

    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10) Chrome/130.0.0.0 Mobile Safari/537.36"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        return {"error": f"Network error: {e}"}

    def get_value(label):
        try:
            div = soup.find("span", string=label).find_parent("div")
            return div.find("p").get_text(strip=True)
        except AttributeError:
            return None

    data = {key: get_value(key) for key in DESIRED_ORDER}
    return data

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "🚗 Vehicle Info API by Mohd Kaif is running!",
        "developer": COPYRIGHT_STRING
    })

@app.route("/lookup", methods=["GET"])
def lookup_vehicle():
    rc_number = request.args.get("rc")
    if not rc_number:
        return jsonify({
            "error": "Please provide ?rc= parameter",
            "copyright": COPYRIGHT_STRING
        }), 400

    details = get_vehicle_details(rc_number)
    ordered_details = OrderedDict()
    for key in DESIRED_ORDER:
        ordered_details[key] = details.get(key)
    ordered_details["copyright"] = COPYRIGHT_STRING
    return jsonify(ordered_details)

# 👇 Required for Vercel (serverless)
if __name__ == "__main__":
    app.run()
