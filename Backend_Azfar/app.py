import os
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from models import db, Item, User

# Establish workspace coordinates relative to this backend script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Frontend_Team"))

app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# Persistent Database Target File Path Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'ecoloop.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ==========================================
# 🌐 WEB PAGE VIEW ENDPOINTS (HTML Serving)
# ==========================================

@app.route("/", methods=["GET"])
def serve_homepage(): return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/login", methods=["GET"])
def serve_login_page(): return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/register", methods=["GET"])
def serve_register_page(): return send_from_directory(FRONTEND_DIR, "register.html")

@app.route("/forgot-password", methods=["GET"])
def serve_forgot_password_page(): return send_from_directory(FRONTEND_DIR, "forgot_password.html")

@app.route("/student", methods=["GET"])
def serve_student_panel(): return send_from_directory(FRONTEND_DIR, "student_panel.html")

@app.route("/dashboard", methods=["GET"])
def serve_student_dashboard(): return send_from_directory(FRONTEND_DIR, "student_dashboard.html")

@app.route("/admin", methods=["GET"])
def serve_admin_panel(): return send_from_directory(FRONTEND_DIR, "admin_panel.html")

@app.route("/style.css", methods=["GET"])
def serve_styles(): return send_from_directory(FRONTEND_DIR, "style.css")

@app.route("/search", methods=["GET"])
def search_items():
    query_param = request.args.get('query', '').strip()
    if query_param:
        search_results = Item.query.filter((Item.name.ilike(f"%{query_param}%")) | (Item.description.ilike(f"%{query_param}%"))).all()
    else:
        search_results = Item.query.all()
    return render_template("result.html", items=search_results, query=query_param)


# ==========================================
# 🔐 AUTHENTICATION ENDPOINTS (Database Link)
# ==========================================

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    
    # Validation: Look for duplicates inside database user rows before saving
    if User.query.filter_by(student_id=data.get("student_id")).first() or User.query.filter_by(email=data.get("email")).first():
        return jsonify({"error": "Account credentials already exist in database matrix."}), 400
        
    new_user = User(
        name=data.get("name"),
        student_id=data.get("student_id"),
        level=data.get("level"),
        email=data.get("email"),
        password=data.get("password")
    )
    db.session.add(new_user)
    db.session.commit() # Permanently writes account info to ecoloop.db file
    return jsonify(new_user.to_dict()), 201

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    user = User.query.filter_by(student_id=data.get("username")).first() or User.query.filter_by(email=data.get("username")).first()
    
    if user and user.password == data.get("password"):
        return jsonify({
            "success": True,
            "user": {
                "name": user.name,
                "student_id": user.student_id,
                "level": user.level,
                "email": user.email
            }
        }), 200
    return jsonify({"error": "Invalid verification credentials supplied."}), 401


# ==========================================
# 📊 DATA INTERACTION ENDPOINTS (JSON API)
# ==========================================

@app.route("/items", methods=["GET"])
def get_items():
    all_items = Item.query.order_by(Item.id.desc()).all()
    return jsonify([item.to_dict() for item in all_items])

@app.route("/items", methods=["POST"])
def add_item():
    data = request.json
    new_item = Item(
        name=data.get("name"),
        price=float(data.get("price")),
        student=data.get("student"),
        level=data.get("level"),
        description=data.get("description", "Pre-loved FCI material.")
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def toggle_item(item_id):
    item = Item.query.get(item_id)
    if not item: return jsonify({"error": "Item not found"}), 404
    
    data = request.json or {}
    buyer_name = data.get("buyer")
    
    item.sold = not item.sold
    item.buyer = buyer_name if item.sold else None
        
    db.session.commit()
    return jsonify(item.to_dict())

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item: return jsonify({"error": "Item not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "operational purge completed successfully"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Automatically generates fresh User and Item tables inside ecoloop.db on startup
    app.run(port=5000, debug=True)