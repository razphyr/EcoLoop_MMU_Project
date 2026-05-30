import os
import random
import pyotp  # Handled for true mathematical TOTP app sync verification
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from models import db, Item, User, Report 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Frontend_Team"))

app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'ecoloop.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ==========================================
# 🌐 HTML STATIC FILE PAGE ROUTERS
# ==========================================
@app.route("/")
def serve_homepage(): 
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/login")
def serve_login_page(): 
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/register")
def serve_register_page(): 
    return send_from_directory(FRONTEND_DIR, "register.html")

@app.route("/forgot-password")
def serve_forgot_password_page(): 
    return send_from_directory(FRONTEND_DIR, "forgot_password.html")

@app.route("/student")
def serve_student_panel(): 
    return send_from_directory(FRONTEND_DIR, "student_panel.html")

@app.route("/dashboard")
def serve_student_dashboard(): 
    return send_from_directory(FRONTEND_DIR, "student_dashboard.html")

@app.route("/admin")
def serve_admin_panel(): 
    return send_from_directory(FRONTEND_DIR, "admin_panel.html")

@app.route("/admin/items")
def serve_admin_moderator_panel():
    return send_from_directory(FRONTEND_DIR, "admin_moderator.html")

@app.route("/product/<int:item_id>")
def serve_product_detail_page(item_id):
    return send_from_directory(FRONTEND_DIR, "product_detail.html")

@app.route("/profile/<string:username>")
def serve_seller_profile_page(username):
    # This serves the generic profile template; the frontend JavaScript reads the URL parameter to populate it
    return send_from_directory(FRONTEND_DIR, "seller_profile.html")


# ==========================================
# 🔍 ECOLOOP DYNAMIC JINJA2 SEARCH ENGINE
# ==========================================
@app.route("/search", methods=["GET"])
def search_marketplace_items():
    query_param = request.args.get("query", "").strip()
    matched_items = Item.query.filter(
        (Item.name.like(f"%{query_param}%")) | 
        (Item.description.like(f"%{query_param}%"))
    ).all()
    return render_template("result.html", query=query_param, items=matched_items)


# ==========================================
# 🔐 ACCOUNT ACCESS & REGISTRATION GATEWAY API
# ==========================================
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    email = data.get("email", "").lower().strip()
    
    if not (email.endswith("@student.mmu.edu.my") or email.endswith("@mmu.edu.my")):
        return jsonify({"error": "Access Denied: Only official MMU email addresses are permitted to register."}), 403
    
    existing_user = User.query.filter((User.email == email) | (User.student_id == data.get("student_id"))).first()
    if existing_user:
        return jsonify({"error": "A profile node with this Email or Student ID already exists."}), 400

    new_user = User(
        name=data.get("name"), 
        student_id=data.get("student_id"),
        level=data.get("level"), 
        email=email, 
        password=data.get("password"),
        role="user"
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Success"}), 201

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    user = User.query.filter((User.email == username) | (User.student_id == username)).first()
    if user and user.password == password:
        return jsonify({
            "success": True,
            "user": {"name": user.name, "student_id": user.student_id, "level": user.level, "role": user.role}
        }), 200
    return jsonify({"error": "Invalid credentials"}), 401


# ==========================================
# 🔑 SECURITY SYSTEM 2FA AUTHENTICATOR API
# ==========================================
@app.route("/api/send-otp", methods=["POST"])
def send_otp():
    email = request.json.get("email")
    user = User.query.filter_by(email=email).first()
    if not user: return jsonify({"error": "Account email node not found inside database records."}), 404
    
    if not user.otp_secret:
        user.otp_secret = pyotp.random_base32()
        db.session.commit()
        
    return jsonify({"success": True, "secret": user.otp_secret})

@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    email = data.get("email")
    token_input = data.get("otp") 
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.otp_secret: return jsonify({"error": "2FA Authenticator node not configured."}), 400
    
    totp = pyotp.TOTP(user.otp_secret)
    if totp.verify(token_input, valid_window=2):
        return jsonify({"success": True, "message": "2FA Clearance Confirmed"})
    return jsonify({"error": "Invalid token pass. Please verify your mobile device clock sync configurations."}), 400

@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    
    user = User.query.filter_by(email=email).first()
    if user:
        user.password = password
        db.session.commit()
        return jsonify({"success": True, "message": "Passcode overwritten successfully."}), 200
    return jsonify({"error": "Failed to update profile parameter node."}), 404


# ==========================================
# 🛡️ SYSTEM FAULT REPORTING & FEEDBACK API
# ==========================================
@app.route("/api/reports", methods=["POST"])
def add_report():
    data = request.json
    new_report = Report(
        type=data.get("type"),
        statement=data.get("statement"),
        image=data.get("image"), 
        user_name=data.get("user_name")
    )
    db.session.add(new_report)
    db.session.commit()
    return jsonify({"message": "Report saved"}), 201

@app.route("/api/reports", methods=["GET"])
def get_reports():
    all_reports = Report.query.all()
    output = []
    for r in all_reports:
        output.append({
            "id": r.id,
            "type": r.type,
            "statement": r.statement,
            "image": r.image,
            "user_name": r.user_name
        })
    return jsonify(output)


# ==========================================
# 📊 CENTRAL ASSET TRADING MARKETPLACE API
# ==========================================
@app.route("/items", methods=["GET"])
def get_items():
    all_items = Item.query.all()
    output = []
    for i in all_items:
        # Cross-Compatible Translation: Maps raw boolean flags back into integer choices for Maathesh arrays
        output.append({
            "id": i.id, 
            "name": i.name, 
            "price": i.price, 
            "student": i.student, 
            "level": i.level if i.level else "Degree", 
            "sold": 1 if i.sold else 0, 
            "description": i.description if i.description else "Ecosystem trade asset.", 
            "buyer": i.buyer,
            "image": getattr(i, "image", None),
            "faculty": i.faculty if i.faculty else "FCI"
        })
    return jsonify(output)

@app.route("/items", methods=["POST"])
def add_item():
    data = request.json
    new_item = Item(
        name=data.get("name"), 
        price=float(data.get("price")), 
        student=data.get("student"), 
        faculty=data.get("faculty", "FCI"),
        level=data.get("level", "Degree"), 
        description=data.get("description", "Ecosystem trade asset."),
        image=data.get("image", None),
        sold=False
    )
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({
        "id": new_item.id,
        "name": new_item.name,
        "price": new_item.price,
        "student": new_item.student,
        "faculty": new_item.faculty,
        "sold": 0
    }), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def toggle_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
        
    data = request.json or {}
    item.sold = not item.sold
    item.buyer = data.get("buyer") if item.sold else None
    db.session.commit()
    
    return jsonify({
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "student": item.student,
        "faculty": item.faculty if item.faculty else "FCI",
        "sold": 1 if item.sold else 0
    })

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return jsonify({"message": "deleted"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="admin@mmu.edu.my").first():
            db.session.add(User(name="Admin Account", student_id="ADMIN1", level="Degree", email="admin@mmu.edu.my", password="test12345", role="admin"))
            db.session.commit()
    app.run(port=5000, debug=True)