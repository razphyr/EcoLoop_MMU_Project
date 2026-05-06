from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Item, User

app = Flask(__name__)
CORS(app) # Enables the connection for Maathesh and Daavinesh's GUI

# 1. Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecoloop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. Initialize Database
db.init_app(app)

# 3. Automatic Table Creation
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "EcoLoop MMU: FCI Faculty Marketplace is Online!"

# 4. Marketplace: View Items (GET) - Filters for FCI & 2 Academic Categories
@app.route('/api/items', methods=['GET'])
def get_items():
    category = request.args.get('category') # 'fd' (Foundation/Diploma) or 'degree'
    

    query = Item.query.filter_by(faculty='FCI')
    
    if category == 'fd':
        query = query.filter(Item.academic_level.in_(['Foundation', 'Diploma']))
    elif category == 'degree':
        query = query.filter_by(academic_level='Degree')
        
    items = query.all()
    
    return jsonify([{
        'id': item.id,
        'title': item.title,
        'price': item.price,
        'original_price': item.originalprice,
        'level': item.academic_level,
        'department': item.department,
        'contact': item.contact_info
    } for item in items])

# 5. Sustainability Brain: Community Impact Metrics (GET)
@app.route('/api/impact', methods=['GET'])
def get_impact():
    fci_items = Item.query.filter_by(faculty='FCI').all()
    reused_count = len(fci_items)
    
    # Calculation Logic: Total Savings = sum of (Original Price - Listing Price)
    total_savings = sum((i.originalprice - i.price) for i in fci_items if i.originalprice and i.price)
            
    return jsonify({
        "fci_community_impact": {
            "total_items_reused": reused_count,
            "student_savings_rm": round(total_savings, 2),
            "co2_offset_kg": reused_count * 0.5 
        },
        "status": "FCI leading the circular economy at MMU."
    })

# 6. User Security: MMU-Exclusive Registration (POST)
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    
    # Validation: Restricted to MMU domains for security
    if not email or not (email.endswith('@mmu.edu.my') or email.endswith('@student.mmu.edu.my')):
        return jsonify({"error": "Registration restricted to MMU accounts only."}), 403

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 400

    new_user = User(
        name=data.get('name'),
        email=email,
        # Secure password hashing
        password=generate_password_hash(data.get('password'), method='pbkdf2:sha256'),
        role="Student"
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"Welcome to FCI EcoLoop, {new_user.name}!"}), 201

# 7. User Security: Secure Login (POST)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    if user and check_password_hash(user.password, data.get('password')):
        return jsonify({"message": "Login successful", "user_id": user.id, "name": user.name}), 200
    
    return jsonify({"error": "Invalid email or password"}), 401

# 8. Marketplace: Post New Resource (POST)
@app.route('/api/items', methods=['POST'])
def add_item():
    data = request.get_json()
    try:
        new_item = Item(
            title=data.get('title'),
            price=float(data.get('price')),
            originalprice=float(data.get('originalprice', 0)),
            description=data.get('description'),
            department=data.get('department'),
            academic_level=data.get('level'), # Expects 'Foundation', 'Diploma', or 'Degree'
            contact_info=data.get('contact'),
            faculty="FCI", # Fixed to FCI to ensure data integrity
            seller_id=data.get('seller_id')
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "FCI Resource successfully listed!"}), 201
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data format. Please check prices."}), 400

# 9. Moderation: Delete Resource (DELETE)
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    # Ensure item exists and belongs to the FCI faculty
    if not item or item.faculty != 'FCI':
        return jsonify({"error": "Resource not found."}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Resource removed from marketplace."}), 200

# 10. Marketplace: Update Resource Details (PUT)
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item or item.faculty != 'FCI':
        return jsonify({"error": "Resource not found."}), 404
        
    data = request.get_json()
    try:
        if 'price' in data: item.price = float(data['price'])
        if 'originalprice' in data: item.originalprice = float(data['originalprice'])
        
        item.title = data.get('title', item.title)
        item.description = data.get('description', item.description)
        item.department = data.get('department', item.department)
        item.academic_level = data.get('level', item.academic_level)
        item.contact_info = data.get('contact_info', item.contact_info)

        db.session.commit()
        return jsonify({"message": f"Resource '{item.title}' updated successfully!"}), 200
    except ValueError:
        return jsonify({"error": "Invalid price format."}), 400

if __name__ == '__main__':
    app.run(debug=True)