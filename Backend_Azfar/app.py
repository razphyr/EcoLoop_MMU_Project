import os
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Establish workspace coordinate paths relative to this backend script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Frontend_Team"))

# Initialize Flask and link the template/static directories cleanly to Frontend_Team
app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# ==========================================
# 💾 PERSISTENT SQLite STORAGE CONFIGURATION
# ==========================================
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'ecoloop.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    student = db.Column(db.String(100), nullable=False)   # Seller name
    level = db.Column(db.String(50), nullable=False)     # 'Degree' or 'Diploma/Foundation'
    sold = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    buyer = db.Column(db.String(100), nullable=True)      # Tracks purchase history

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "student": self.student,
            "level": self.level,
            "sold": self.sold,
            "description": self.description,
            "buyer": self.buyer
        }

# ==========================================
# 🌐 WEB PAGE VIEW ENDPOINTS (HTML Serving)
# ==========================================

@app.route("/", methods=["GET"])
def serve_homepage():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/login", methods=["GET"])
def serve_login_page():
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/register", methods=["GET"])
def serve_register_page():
    return send_from_directory(FRONTEND_DIR, "register.html")

@app.route("/forgot-password", methods=["GET"])
def serve_forgot_password_page():
    return send_from_directory(FRONTEND_DIR, "forgot_password.html")

@app.route("/student", methods=["GET"])
def serve_student_panel():
    return send_from_directory(FRONTEND_DIR, "student_panel.html")

@app.route("/admin", methods=["GET"])
def serve_admin_panel():
    return send_from_directory(FRONTEND_DIR, "admin_panel.html")

@app.route("/style.css", methods=["GET"])
def serve_styles():
    return send_from_directory(FRONTEND_DIR, "style.css")

@app.route("/search", methods=["GET"])
def search_items():
    query_param = request.args.get('query', '').strip()
    if query_param:
        # Queries rows with case-insensitive filters checking the name or description columns
        search_results = Item.query.filter(
            (Item.name.ilike(f"%{query_param}%")) | 
            (Item.description.ilike(f"%{query_param}%"))
        ).all()
    else:
        search_results = Item.query.all()
    return render_template("result.html", items=search_results, query=query_param)

# ==========================================
# 📊 FCI DATA API SYSTEM HANDLERS (JSON API)
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
        description=data.get("description", "Pre-loved FCI academic material.")
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def toggle_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "FCI tracking reference matrix index not discovered"}), 404
    
    data = request.json or {}
    buyer_name = data.get("buyer")
    
    item.sold = not item.sold
    if item.sold:
        item.buyer = buyer_name if buyer_name else "FCI Marketplace User"
    else:
        item.buyer = None
        
    db.session.commit()
    return jsonify(item.to_dict())

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "FCI tracking reference matrix index not discovered"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Target data item cleanly purged from storage database."})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)