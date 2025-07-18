from flask import Flask, request, jsonify, send_file
from cloudant.client import Cloudant
from cloudant.error import CloudantException
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Cloudant credentials
apikey = os.getenv('apikey')
url = os.getenv('url')
username = os.getenv('username')
db_name = os.getenv('db_name')

# Connect to Cloudant
client = Cloudant.iam(username, apikey, url=url, connect=True)
try:
    db = client[db_name]
except CloudantException:
    db = client.create_database(db_name)

# Serve static HTML directly from current folder
@app.route('/')
def index():
    return send_file("index.html")

@app.route('/create', methods=['POST'])
def create_record():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        feedback = data.get('feedback')

        if not name or not email or not feedback:
            return jsonify({"error": "Missing name, email, or feedback"}), 400

        document = {
            "name": name,
            "email": email,
            "feedback": feedback
        }
        db.create_document(document)
        return jsonify({"message": "Record created successfully!"}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/get_records', methods=['GET'])
def get_records():
    records = []
    for doc in db:
        records.append({
            "name": doc.get("name"),
            "email": doc.get("email"),
            "feedback": doc.get("feedback")
        })
    return jsonify(records), 200

if __name__ == '__main__':
    app.run(debug=True)