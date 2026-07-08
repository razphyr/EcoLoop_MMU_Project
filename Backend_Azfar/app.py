import os
import random
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from models import db, Item, User, Report
from datetime import datetime, timedelta

# =======================================================
# 1. DEFINE BASE PATHS
# =======================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Frontend_Team"))

# =======================================================
# 2. INITIALIZE FLASK ENGINE & CROSS-ORIGIN MIDDLEWARE
# =======================================================
app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# =======================================================
# 3. REINFORCED PRODUCTION POSTGRES DATA LINK POOLING
# =======================================================
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    if "?sslmode=" not in DATABASE_URL:
        DATABASE_URL += "?sslmode=require"
        
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'ecoloop.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "pool_recycle": 280,
    "pool_size": 10,
    "max_overflow": 5
}

# =======================================================
# 4. SECURE SMTP CLiC EMAIL DISPATCH INFRASTRUCTURE
# =======================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD") 

def dispatch_secure_otp(recipient_email, otp_code):
    """Physically transmits an official security token matching CLiC email formats."""
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("⚠️ MAIL WARNING: SMTP access keys missing from Render Environment panel.")
        return False
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = "🔐 CLiC Portal Access: Security Verification Token"
        
        html_body = f"""
        <html>
          <body style="font-family: Arial, sans-serif; font-size: 14px; color: #333; line-height: 1.5;">
            <p>Dear {recipient_email.split('@')[0].upper()},</p>
            
            <p>To complete <b>login process to CLiC</b>, please use <b>6 digits OTP code</b> provided as below. 
            Valid <b>10 minutes</b>.</p>
            
            <p style="font-size: 22px; font-weight: bold; letter-spacing: 1px; margin: 20px 0; color: #000;">
              {otp_code}
            </p>
            
            <p>Thank you.</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(html_body, 'html'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
        server.quit()
        print(f"✅ SUCCESS: Security token delivered to {recipient_email}")
        return True
    except Exception as e:
        print(f"🚨 MAIL ENGINE DISPATCH CRITICAL FAULT: {e}")
        return False

# =======================================================
# 5. INITIALIZE MATRIX DATABASE
# =======================================================
db.init_app(app)

with app.app_context():
    db.create_all()
    db.session.commit()
    db.engine.dispose()

LIVE_OTP_REGISTRY = {}

# =======================================================
# 🛣️ STATIC FILE ROUTING CONTROLLERS
# =======================================================
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

# =======================================================
# 👤 USER PROFILE API
# =======================================================
@app.route("/api/user/<string:username>", methods=["GET"])
def get_user_profile_data(username):
    user_record = User.query.filter_by(name=username).first()
    if not user_record: 
        return jsonify({"error": "User profile node not located."}), 404
        
    requester_role = request.args.get("role", "user").lower().strip()
    requester_name = request.args.get("requester", "").strip()

    if requester_role == "admin" or requester_name == user_record.name:
        return jsonify({
            "name": user_record.name,
            "email": user_record.email,
            "level": user_record.level,
            "phone": user_record.phone if user_record.phone else "Not Supplied",
            "role": user_record.role
        }), 200
        
    return jsonify({
        "name": user_record.name,
        "level": user_record.level,
        "email": "[PROTECTED - ADMIN ONLY]",
        "phone": "[PROTECTED - ADMIN ONLY]",
        "role": user_record.role
    }), 200

@app.route("/api/user/<string:username>", methods=["PUT"])
def update_user_profile_data(username):
    user = User.query.filter_by(name=username).first()
    if not user: 
        return jsonify({"error": "User record missing."}), 404
        
    data = request.json or {}
    user.phone = data.get("phone", "").strip()
    db.session.commit()
    return jsonify({"success": True, "message": "Profile parameters updated."}), 200

# =======================================================
# 🔍 ECOLOOP MARKETPLACE SEARCH ENGINE
# =======================================================
@app.route("/search", methods=["GET"])
def search_marketplace_items():
    query_param = request.args.get("query", "").strip()
    matched_items = Item.query.filter(
        (Item.name.like(f"%{query_param}%")) | 
        (Item.description.like(f"%{query_param}%"))
    ).all()
    return render_template("result.html", query=query_param, items=matched_items)

# =======================================================
# 🔐 SYSTEM REGISTRATION & ACCOUNT API
# =======================================================
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    email = data.get("email", "").lower().strip()
    
    if not (email.endswith("@student.mmu.edu.my") or email.endswith("@mmu.edu.my") or email.endswith("@gmail.com")):
        return jsonify({"error": "Access Denied: Please use a valid email structure."}), 403
    
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

# =======================================================
# 🔓 SECURE LOGIN ROUTE (GENERATES & MAILS REAL OTP)
# =======================================================
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    
    user = User.query.filter((User.email == username) | (User.student_id == username)).first()
    
    if user and user.password == password:
        generated_code = str(random.randint(100000, 999999))
        LIVE_OTP_REGISTRY[user.email] = {"code": generated_code}
        
        # Fires the email directly to your recipient outbox
        dispatch_secure_otp(user.email, generated_code)
        
        return jsonify({
            "action": "otp_required",
            "email": user.email,
            "simulated_token": generated_code,
            "recipient_name": user.name.upper()
        }), 200
        
    return jsonify({"error": "Invalid login credentials configuration string."}), 401

@app.route("/api/send-otp", methods=["POST"])
def api_send_otp():
    data = request.json or {}
    email = data.get("email", "").lower().strip()
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "FCI Identity Fault: This email destination does not exist."}), 444

    generated_otp = str(random.randint(100000, 999999))
    LIVE_OTP_REGISTRY[email] = {"code": generated_otp}
    
    dispatch_secure_otp(email, generated_otp)
    
    return jsonify({
        "success": True, 
        "message": "Security token successfully outputted.",
        "secret": f"MMU-SECURE-SEED-{generated_otp[:3]}-{generated_otp[3:]}"
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
        
    return jsonify({"error": "Invalid 6-digit verification code."}), 400

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
    return jsonify({"error": "Failed to update profile parameters."}), 404

# =======================================================
# 🛡️ HELPDESK & TICKETING API
# =======================================================
@app.route("/api/reports", methods=["POST"])
def add_report():
    db.session.add(Report(type=request.json.get("type"), statement=request.json.get("statement"), image=request.json.get("image"), user_name=request.json.get("user_name")))
    db.session.commit()
    return jsonify({"message": "saved"}), 201

@app.route("/api/reports", methods=["GET"])
def get_reports():
    return jsonify([{"id":r.id, "type":r.type, "statement":r.statement, "image":r.image, "user_name":r.user_name} for r in Report.query.all()])

@app.route("/api/reports/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    report = Report.query.get(report_id)
    if report:
        db.session.delete(report)
        db.session.commit()
    return jsonify({"message": "deleted"}), 200

# =======================================================
# 📊 CENTRAL ASSET TRADING MARKETPLACE API
# =======================================================
@app.route("/items", methods=["GET"])
def get_items():
    return jsonify([{
        "id": i.id, "name": i.name, "price": i.price, "student": i.student, "level": i.level, 
        "description": i.description, "buyer": i.buyer, "image": getattr(i, "image", None),
        "faculty": i.faculty, "fee_deducted": getattr(i, "fee_deducted", 0.0),
        "final_payout": getattr(i, "final_payout", 0.0), "status": getattr(i, "status", "available"),
        "delivery_proof": getattr(i, "delivery_proof", None), "published_date": getattr(i, "published_date", "16-Jun-2026") 
    } for i in Item.query.all()]), 200
    
@app.route("/items", methods=["POST"])
def add_item():
    data = request.json
    live_timestamp_string = datetime.now().strftime("%d-%b-%Y")
    new_item = Item(
        name=data.get("name"), price=float(data.get("price")), student=data.get("student"), 
        faculty=data.get("faculty", "FCI"), level=data.get("level", "Degree"), 
        description=data.get("description"), image=data.get("image"), status="available",
        published_date=live_timestamp_string 
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"id": new_item.id, "name": new_item.name, "price": new_item.price, "status": new_item.status}), 201    

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
    item.fee_deducted = round(item.price * 0.06, 2)
    item.final_payout = round(item.price - item.fee_deducted, 2)
    
    db.session.commit()
    return jsonify({"success": True, "id": item.id, "status": item.status}), 200

@app.route("/items/<int:item_id>/confirm-sold", methods=["POST"])
def confirm_item_sold(item_id):
    item = Item.query.get(item_id)
    if not item: return jsonify({"error": "Item not found."}), 404
    data = request.json or {}
    proof_image = data.get("delivery_proof")
    if not proof_image: return jsonify({"error": "Visual proof required."}), 400
    if item.status != "pending": return jsonify({"error": "Invalid state."}), 400
    
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

# =======================================================
# 🚀 BOOT ENGINE CONTEXT
# =======================================================
if __name__ == "__main__":
    with app.app_context():
        if not User.query.filter_by(email="admin@mmu.edu.my").first():
            db.session.add(User(name="Admin Account", student_id="ADMIN1", level="Degree", email="admin@mmu.edu.my", password="test12345", role="admin"))
            db.session.commit()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)