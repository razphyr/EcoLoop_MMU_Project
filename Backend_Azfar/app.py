from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Item, User 

app = Flask(__name__)
CORS(app) # Allows the frontend to talk to this API

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecoloop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/api/items', methods=['GET'])
def get_items():
    items = Item.query.filter_by(faculty='FCI').all()
    # We map 'title' to 'name' to match your results.html exactly
    return jsonify([{
        'name': i.title, 
        'description': i.description,
        'faculty': i.faculty
    } for i in items])

@app.route('/api/impact', methods=['GET'])
def get_impact():
    fci_items = Item.query.filter_by(faculty='FCI').all()
    count = len(fci_items)
    # Total CO2 offset calculation:
    # $$Impact = Reused\_Items \times 0.5\text{kg}$$
    return jsonify({
        "fci_community_impact": {
            "total_items_reused": count,
            "co2_offset_kg": count * 0.5 
        }
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)