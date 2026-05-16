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
    # Capture the query parameters from the URL
    query = request.args.get('query', '').lower()
    level = request.args.get('level', 'All')

    # Start with a base query
    base_query = Item.query.filter_by(faculty='FCI')

    # Apply the academic level filter if it's not "All"
    if level != 'All':
        base_query = base_query.filter_by(level=level)

    items = base_query.all()

    # Simple keyword search logic
    results = []
    for i in items:
        if query in i.title.lower() or query in i.description.lower():
            results.append({
                'name': i.title,
                'description': i.description,
                'faculty': i.faculty,
                'level': i.level,
                'price': i.price,
                'contact': i.contact_info
            })
    
    return jsonify(results)

@app.route('/api/add-item', methods=['POST'])
def add_item():
    data = request.get_json()
    
    # Basic validation
    if not data.get('title') or not data.get('price'):
        return jsonify({"error": "Title and Price are required"}), 400

    new_item = Item(
        title=data.get('title'),
        price=float(data.get('price')),
        originalprice=float(data.get('originalprice', 0)),
        description=data.get('description'),
        faculty='FCI',
        level=data.get('level', 'Degree'),
        category=data.get('category', 'General'),
        contact_info=data.get('contact'),
        owner_email=data.get('email'), # Track who listed it
        status="Available"
    )
    
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Item listed successfully on EcoLoop!"}), 201

@app.route('/api/impact', methods=['GET'])
def get_impact():
    all_items = Item.query.filter_by(faculty='FCI').all()
    
    total_co2 = 0
    for item in all_items:
        if item.category == 'Electronics' or 'Kit' in item.title:
            total_co2 += 1.5
        elif item.category == 'Book':
            total_co2 += 0.3
        else:
            total_co2 += 0.5 # Default
            
    return jsonify({
        "fci_community_impact": {
            "total_items_reused": len(all_items),
            "co2_offset_kg": round(total_co2, 2)
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

# app.py Get items listed by a specific student
@app.route('/api/my-items', methods=['GET'])
def get_my_items():
    email = request.args.get('email')
    items = Item.query.filter_by(owner_email=email).all()
    return jsonify([{
        'id': i.id,
        'title': i.title,
        'status': i.status,
        'price': i.price
    } for i in items])

if __name__ == '__main__':
    app.run(port=5000, debug=True)