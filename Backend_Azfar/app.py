import os
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
# Imported Report model cleanly here
from models import db, Item, User, Report 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Frontend_Team"))

app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'ecoloop.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ==========================================
# 🌐 BASIC HTML PAGE PAGES ROUTING
# ==========================================
@app.route("/")
def serve_homepage(): return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/login")
def serve_login_page(): return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/register")
def serve_register_page(): return send_from_directory(FRONTEND_DIR, "register.html")

@app.route("/student")
def serve_student_panel(): return send_from_directory(FRONTEND_DIR, "student_panel.html")

@app.route("/dashboard")
def serve_student_dashboard(): return send_from_directory(FRONTEND_DIR, "student_dashboard.html")

@app.route("/admin")
def serve_admin_panel(): return send_from_directory(FRONTEND_DIR, "admin_panel.html")


# ==========================================
# 🔐 ACCOUNT AUTHENTICATION API
# ==========================================
@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.json
    new_user = User(
        name=data.get("name"), student_id=data.get("student_id"),
        level=data.get("level"), email=data.get("email"), password=data.get("password"),
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
# 🛡️ NEW REPORT & FEEDBACK HANDLERS API
# ==========================================
@app.route("/api/reports", methods=["POST"])
def add_report():
    data = request.json
    new_report = Report(
        type=data.get("type"),
        statement=data.get("statement"),
        image=data.get("image"), # Receives simple base64 string image data payload
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
# 📊 MARKETPLACE DATA HANDLING API
# ==========================================
@app.route("/items", methods=["GET"])
def get_items():
    all_items = Item.query.all()
    output = []
    for i in all_items:
        output.append({"id": i.id, "name": i.name, "price": i.price, "student": i.student, "level": i.level, "sold": i.sold, "description": i.description, "buyer": i.buyer})
    return jsonify(output)

@app.route("/items", methods=["POST"])
def add_item():
    data = request.json
    new_item = Item(name=data.get("name"), price=float(data.get("price")), student=data.get("student"), level=data.get("level"), description=data.get("description"))
    db.session.add(new_item)
    db.session.commit()
    return jsonify({"message": "Added"}), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def toggle_item(item_id):
    item = Item.query.get(item_id)
    data = request.json or {}
    item.sold = not item.sold
    item.buyer = data.get("buyer") if item.sold else None
    db.session.commit()
    return jsonify({"message": "Toggled"})

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Deleted"})


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="admin@mmu.edu.my").first():
            db.session.add(User(name="Admin Account", student_id="ADMIN1", level="Degree", email="admin@mmu.edu.my", password="test12345", role="admin"))
            db.session.commit()
    app.run(port=5000, debug=True)