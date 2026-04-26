from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Item, User

app = Flask(__name__)

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
    return "EcoLoop MMU: FCI Marketplace is Online!"

# 4. Marketplace: View All Items (GET)
# Features: FCI Filtering & Department Categorization
@app.route('/api/items', methods=['GET'])
def get_items():
    dept_query = request.args.get('dept')
    
    # Gatekeeper: filtering only for the FCI faculty
    query = Item.query.filter_by(faculty='FCI')
    
    if dept_query:
        query = query.filter_by(department=dept_query)
        
    items = query.all()
    
    # Return data structured for GUI 'Item Cards' from here
    return jsonify([{
        'id': item.id,
        'title': item.title,
        'price': item.price,
        'original_price': item.originalprice,
        'description': item.description,
        'department': item.department,
        'contact': item.contact_info
    } for item in items])

# 5. Sustainability Brain: Impact Metrics (GET)
@app.route('/api/impact', methods=['GET'])
def get_impact():
    fci_items = Item.query.filter_by(faculty='FCI').all()
    reused_count = len(fci_items)
    
    # Logic: Total Savings = sum of (Original Price - Listing Price)
    total_savings = sum((i.originalprice - i.price) for i in fci_items if i.originalprice and i.price)
            
    return jsonify({
        "fci_community_impact": {
            "total_items_reused": reused_count,
            "student_savings_rm": round(total_savings, 2),
            "co2_offset_kg": reused_count * 0.5 
        },
        "status": "FCI leading the circular economy."
    })

# 6. User Security: Registration 
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    
    # Validation: Restricted to MMU domains
    if not email or not (email.endswith('@mmu.edu.my') or email.endswith('@student.mmu.edu.my')):
        return jsonify({"error": "Registration restricted to MMU accounts only."}), 403

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 400

    new_user = User(
        name=data.get('name'),
        email=email,
        # Securely hash the password before saving
        password=generate_password_hash(data.get('password'), method='pbkdf2:sha256'),
        role="Student"
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"Welcome {new_user.name}! Your account is ready."}), 201

# 7. User Security: Login (POST)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()

    # Security check
    if user and check_password_hash(user.password, data.get('password')):
        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "name": user.name
        }), 200
    
    return jsonify({"error": "Invalid email or password"}), 401

# 8. Marketplace: Post New Item 
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
            contact_info=data.get('contact'),
            faculty="FCI",
            seller_id=data.get('seller_id')
        )
        db.session.add(new_item)
        db.session.commit()
        return jsonify({"message": "Item successfully listed!"}), 201
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid data format. Check prices and IDs."}), 400

# 9. Moderation: Delete Item 
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found."}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed from marketplace."}), 200

# 10. Update Item Logic 
@app.route('/api/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
        
    data = request.get_json()
    
    # Update fields only if they are provided in the request
    item.title = data.get('title', item.title)
    item.price = float(data.get('price', item.price))
    item.originalprice = float(data.get('originalprice', item.originalprice))
    item.description = data.get('description', item.description)
    item.department = data.get('department', item.department)
    item.contact_info = data.get('contact_info', item.contact_info)

    db.session.commit()
    return jsonify({"message": f"Item '{item.title}' updated successfully!"}), 200

if __name__ == '__main__':
    # Set to debug=True for development on localhost
    app.run(debug=True)