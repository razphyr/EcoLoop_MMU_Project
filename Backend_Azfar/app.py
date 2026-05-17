import os
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Track path locations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "Frontend_Team"))

# ==========================================
# 🌐 WEB PAGE ROUTES (Serves your GUI panels)
# ==========================================

@app.route("/", methods=["GET"])
def serve_homepage():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/student", methods=["GET"])
def serve_student_panel():
    return send_from_directory(FRONTEND_DIR, "student panel.html")

@app.route("/admin", methods=["GET"])
def serve_admin_panel():
    return send_from_directory(FRONTEND_DIR, "admin panel.html")

@app.route("/style.css", methods=["GET"])
def serve_styles():
    return send_from_directory(FRONTEND_DIR, "style.css")



# ==========================================
# 📊 DATA API ROUTES (Handles JSON communication)
# ==========================================

items = [
    {"id": 1, "name": "Notebook", "price": 10, "student": "Ali", "faculty": "FCI", "sold": False},
    {"id": 2, "name": "Calculator", "price": 50, "student": "Siti", "faculty": "FOAIE", "sold": True}
]

@app.route("/items", methods=["GET"])
def get_items():
    return jsonify(items)

@app.route("/items", methods=["POST"])
def add_item():
    data = request.json
    new_item = {
        "id": max([i["id"] for i in items]) + 1 if items else 1,
        "name": data.get("name"),
        "price": data.get("price"),
        "student": data.get("student"),
        "faculty": data.get("faculty"),
        "sold": False
    }
    items.append(new_item)
    return jsonify(new_item)

@app.route("/items/<int:item_id>", methods=["PUT"])
def toggle_item(item_id):
    for i in items:
        if i["id"] == item_id:
            i["sold"] = not i["sold"]
            return jsonify(i)
    return jsonify({"error": "Item not found"}), 404

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    global items
    items = [i for i in items if i["id"] != item_id]
    return jsonify({"message": "deleted"})

if __name__ == "__main__":
    # DIAGNOSTIC PATH PRINTS
    print("\n" + "="*50)
    print(f"LOOKING FOR FRONTEND AT: {FRONTEND_DIR}")
    print(f"DOES THE FOLDER EXIST?:  {os.path.exists(FRONTEND_DIR)}")
    print("="*50 + "\n")
    
    app.run(port=5000, debug=True)