import random
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Item, User 

app = Flask(__name__)
CORS(app) 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecoloop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/api/items', methods=['GET'])
def get_items():
    items = Item.query.filter_by(faculty='FCI').all()
    return jsonify([{
        'name': i.title, 
        'description': i.description,
        'faculty': i.faculty,
        'price': i.price,
        'contact': i.contact_info
    } for i in items])

@app.route('/api/impact', methods=['GET'])
def get_impact():
    fci_items = Item.query.filter_by(faculty='FCI').all()
    count = len(fci_items)
    return jsonify({
        "fci_community_impact": {
            "total_items_reused": count,
            "co2_offset_kg": count * 0.5 
        }
    })

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '')
    
    if not (email.endswith('@student.mmu.edu.my') or email.endswith('@mmu.edu.my')):
        return jsonify({"error": "Registration restricted to MMU emails only."}), 403

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Account already exists."}), 400

    code = str(random.randint(100000, 999999))
    new_user = User(
        name=data.get('name'),
        email=email,
        password=generate_password_hash(data.get('password'), method='pbkdf2:sha256'),
        verification_code=code,
        is_verified=False
    )
    db.session.add(new_user)
    db.session.commit()
    
    print(f"--- [2FA LOG] Code for {email} is {code} ---")
    return jsonify({"message": "Verification code generated!"}), 201

@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if user and user.verification_code == data.get('code'):
        user.is_verified = True
        user.verification_code = None
        db.session.commit()
        return jsonify({"message": "Verified!"}), 200
    return jsonify({"error": "Invalid verification code."}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()
    if user and check_password_hash(user.password, data.get('password')):
        if not user.is_verified:
            return jsonify({"error": "Account not verified."}), 401
        return jsonify({"message": "Success", "user": {"name": user.name}}), 200
    return jsonify({"error": "Invalid email or password"}), 401

if __name__ == '__main__':
    app.run(port=5000, debug=True)