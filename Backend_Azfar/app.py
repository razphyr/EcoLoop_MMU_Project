import os
from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Configure layout directories relative to this file location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Frontend_Team"))

# Initialize Flask and point template/static configurations straight to Frontend_Team
app = Flask(__name__, template_folder=FRONTEND_DIR, static_folder=FRONTEND_DIR, static_url_path='')
CORS(app)

# ==========================================
# 💾 PERSISTENT DATABASE STORAGE ENGINE
# ==========================================
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'ecoloop.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    student = db.Column(db.String(100), nullable=False)  # Seller (Student or Staff member)
    faculty = db.Column(db.String(20), nullable=False)
    sold = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    buyer = db.Column(db.String(100), nullable=True)     # Tracks transaction history

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "student": self.student,
            "faculty": self.faculty,
            "sold": self.sold,
            "description": self.description,
            "buyer": self.buyer
        }

# ==========================================
# 🌐 ROUTING ENDPOINTS (Serves HTML Layouts)
# ==========================================

@app.route("/", methods=["GET"])
def serve_homepage():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/student", methods=["GET"])
def serve_student_panel():
    return send_from_directory(FRONTEND_DIR, "student_panel.html")

@app.route("/dashboard", methods=["GET"])
def serve_student_dashboard():
    # Private user dashboard for Student/Staff purchase tracking & wishlists
    return send_from_directory(FRONTEND_DIR, "student_dashboard.html")

@app.route("/admin", methods=["GET"])
def serve_admin_panel():
    # Restricted server route accessible only by system managers
    return send_from_directory(FRONTEND_DIR, "admin_panel.html")

@app.route("/style.css", methods=["GET"])
def serve_styles():
    return send_from_directory(FRONTEND_DIR, "style.css")

@app.route("/search", methods=["GET"])
def search_items():
    query_param = request.args.get('query', '').strip()
    if query_param:
        search_results = Item.query.filter(
            (Item.name.ilike(f"%{query_param}%")) | 
            (Item.description.ilike(f"%{query_param}%"))
        ).all()
    else:
        search_results = Item.query.all()
    return render_template("result.html", items=search_results, query=query_param)

# ==========================================
# 📊 CLIENT PIPELINE DATA ACTIONS (JSON API)
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
        faculty=data.get("faculty"),
        description=data.get("description", "Pre-loved campus asset.")
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(new_item.to_dict()), 201

@app.route("/items/<int:item_id>", methods=["PUT"])
def toggle_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item index matrix not found"}), 404
    
    data = request.json or {}
    buyer_name = data.get("buyer")
    
    item.sold = not item.sold
    if item.sold:
        item.buyer = buyer_name if buyer_name else "Azfar Hakim"
    else:
        item.buyer = None # Resets entry if item is toggled back to available
        
    db.session.commit()
    return jsonify(item.to_dict())

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item index matrix not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "purge completed"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000, debug=True)