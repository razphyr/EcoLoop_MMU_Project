import os
import random
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

LIVE_OTP_REGISTRY = {}

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
    return send_from_directory(FRONTEND_DIR, "seller_profile.html")

@app.route("/verify-login-otp")
def serve_login_otp_verification_view(): 
    return send_from_directory(FRONTEND_DIR, "verify_otp.html")


# ==========================================
# 👤 USER ACCOUNT DATA SETTINGS MODULE API
# ==========================================
@app.route("/api/user/<string:username>", methods=["GET"])
def get_user_profile_data(username):
    user = User.query.filter_by(name=username).first()
    if not user: 
        return jsonify({"error": "User profile node not located."}), 404
    return jsonify({
        "name": user.name,
        "email": user.email,
        "level": user.level,
        "phone": user.phone if user.phone else ""
    }), 200

@app.route("/api/user/<string:username>", methods=["PUT"])
def update_user_profile_data(username):
    user = User.query.filter_by(name=username).first()
    if not user: 
        return jsonify({"error": "User record missing."}), 404
        
    data = request.json or {}
    user.phone = data.get("phone", "").strip()
    db.session.commit()
    
    return jsonify({"success": True, "message": "Phone parameters synchronized successfully."}), 200


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
# 🔐 SECURE STREAMLINED IN-PLATFORM AUTHENTICATION API
# ==========================================
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    email = data.get("email", "").lower().strip()
    
    if not (email.endswith("@student.mmu.edu.my") or email.endswith("@mmu.edu.my") or email.endswith("@gmail.com")):
        return jsonify({"error": "Access Denied: Please use a valid email schema node."}), 403
    
    existing_user = User.query.filter((User.email == email) | (User.student_id == data.get("student_id"))).first()
    if existing_user: 
        return jsonify({"error": "Profile records exist."}), 400

    new_user = User(
        name=data.get("name"), student_id=data.get("student_id"),
        level=data.get("level"), email=email, password=data.get("password"), role="user"
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
        generated_code = str(random.randint(100000, 999999))
        LIVE_OTP_REGISTRY[user.email] = {"code": generated_code}
        
        print("\n" + "="*60)
        print(f"🚨 CLiC SECURITY ENGINE")
        print(f"📥 OTP DISPATCH TARGET: {user.email}")
        print(f"🔢 SYSTEM PASSCODE TOKEN: {generated_code}")
        print("="*60 + "\n")
        
        return jsonify({
            "action": "otp_required",
            "email": user.email,
            "simulated_token": generated_code,
            "recipient_name": user.name.upper()
        }), 200
        
    return jsonify({"error": "Invalid login credentials configuration string."}), 401


# =======================================================
# 🔐 TWO-FACTOR AUTHENTICATION SYSTEM & TERMINAL DISPATCH
# =======================================================
@app.route("/api/send-otp", methods=["POST"])
def api_send_otp():
    data = request.json or {}
    email = data.get("email", "").lower().strip()
    
    # 🔍 Verify user exists inside your SQLite records
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "FCI Identity Fault: This email destination does not exist."}), 444

    # 🔢 Generate a fresh 6-digit secure token
    generated_otp = str(random.randint(100000, 999999))
    
    # 💾 Cache the code in memory for verification validation checks
    LIVE_OTP_REGISTRY[email] = {"code": generated_otp}
    
    # 📟 GRAPHICAL TERMINAL BROADCAST INTERCEPT ENGINE
    print("\n" + "═"*60)
    print(" 🛡️  SECURITY MATRIX INTERCEPT: TWO-FACTOR VERIFICATION GENERATED")
    print(f" 📥 TARGET MAIL ADDRESS NODE : {email}")
    print(f" 🔢 SYSTEM PASSCODE TOKEN    : {generated_otp}")
    print("═"*60 + "\n")
    
    return jsonify({
        "success": True, 
        "message": "Security token outputted to active server terminal lines.",
        "secret": f"MMU-SECURE-SEED-{generated_otp[:3]}-{generated_otp[3:]}" # Formatted for your HTML secret key text holder block
    }), 200


@app.route("/api/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json or {}
    email = data.get("email", "").lower().strip()
    token_input = data.get("otp", "").strip()
    
    user = User.query.filter_by(email=email).first()
    if not user: 
        return jsonify({"error": "User account node missing."}), 404
        
    cached_record = LIVE_OTP_REGISTRY.get(email)
    
    if cached_record and cached_record["code"] == token_input:
        LIVE_OTP_REGISTRY.pop(email, None) 
        return jsonify({
            "success": True, 
            "user": {"name": user.name, "student_id": user.student_id, "level": user.level, "role": user.role}
        }), 200
        
    return jsonify({"error": "Invalid 6-digit verification code. Please check your backend terminal console."}), 400


@app.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.json or {}
    email = data.get("email", "").lower().strip()
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
    db.session.add(Report(type=request.json.get("type"), statement=request.json.get("statement"), image=request.json.get("image"), user_name=request.json.get("user_name")))
    db.session.commit()
    return jsonify({"message": "saved"}), 201

@app.route("/api/reports", methods=["GET"])
def get_reports():
    return jsonify([{"id":r.id, "type":r.type, "statement":r.statement, "image":r.image, "user_name":r.user_name} for r in Report.query.all()])


# ==========================================
# 📊 CENTRAL ASSET TRADING MARKETPLACE API
# ==========================================
@app.route("/items", methods=["GET"])
def get_items():
    return jsonify([{
        "id": i.id, 
        "name": i.name, 
        "price": i.price, 
        "student": i.student, 
        "level": i.level, 
        "description": i.description, 
        "buyer": i.buyer, 
        "image": getattr(i, "image", None),
        "faculty": i.faculty,
        "fee_deducted": getattr(i, "fee_deducted", 0.0),
        "final_payout": getattr(i, "final_payout", 0.0),
        "status": getattr(i, "status", "available"),
        "delivery_proof": getattr(i, "delivery_proof", None)
    } for i in Item.query.all()]), 200

@app.route("/items", methods=["POST"])
def add_item():
    data = request.json
    new_item = Item(
        name=data.get("name"), 
        price=float(data.get("price")), 
        student=data.get("student"), 
        faculty=data.get("faculty", "FCI"), 
        level=data.get("level", "Degree"), 
        description=data.get("description"), 
        image=data.get("image"), 
        status="available" 
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"id": new_item.id, "name": new_item.name, "price": new_item.price, "status": new_item.status}), 201


# =========================================================
#  💳 RESERVATION ROUTE: Changes status from available -> pending
#==========================================================  
@app.route("/items/<int:item_id>", methods=["PUT"])
def toggle_item(item_id):
    item = Item.query.get(item_id)
    if not item: 
        return jsonify({"error": "Target marketplace asset missing."}), 404
    
    data = request.json or {}
    buyer_name = data.get("buyer")
    
    if item.status != "available":
        return jsonify({"error": "Item is already reserved or sold."}), 400
        
    item.status = "pending"
    item.buyer = buyer_name
    
    # 6% Platform calculation logic parameters
    item.fee_deducted = round(item.price * 0.06, 2)
    item.final_payout = round(item.price - item.fee_deducted, 2)
    
    db.session.commit()
    
    return jsonify({
        "success": True,
        "id": item.id, 
        "status": item.status,
        "buyer": item.buyer,
        "fee_charged": item.fee_deducted,
        "net_payout": item.final_payout
    }), 200


# 📸 FULFILLMENT CLEARANCE: Changes status from pending -> sold
@app.route("/items/<int:item_id>/confirm-sold", methods=["POST"])
def confirm_item_sold(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found."}), 404
        
    data = request.json or {}
    proof_image = data.get("delivery_proof")
    
    if not proof_image:
        return jsonify({"error": "Visual picture proof is mandatory to release platform funds."}), 400
        
    if item.status != "pending":
        return jsonify({"error": "Only pending transaction rows can be finalized."}), 400
        
    item.status = "sold"
    item.delivery_proof = proof_image
    
    db.session.commit()
    return jsonify({"success": True, "status": "sold"}), 200


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