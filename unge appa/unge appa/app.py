from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("ecoloop.db")
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
CORS(app)



@app.route("/items", methods=["GET"])
def get_items():
    conn = get_db_connection()
    items = conn.execute("SELECT * FROM items").fetchall()
    conn.close()

    return jsonify([dict(i) for i in items])

@app.route("/items", methods=["POST"])
def add_item():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO items (name, price, student, faculty, sold)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.get("name"),
        data.get("price"),
        data.get("student"),
        data.get("faculty"),
        0
    ))

    conn.commit()

    # get the newly created item
    item_id = cursor.lastrowid
    new_item = conn.execute(
        "SELECT * FROM items WHERE id = ?",
        (item_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(new_item))

@app.route("/items/<int:item_id>", methods=["PUT"])
def toggle_item(item_id):
    conn = get_db_connection()

    item = conn.execute(
        "SELECT * FROM items WHERE id = ?",
        (item_id,)
    ).fetchone()

    if item is None:
        conn.close()
        return jsonify({"error": "Item not found"}), 404

    new_status = 0 if item["sold"] == 1 else 1

    conn.execute(
        "UPDATE items SET sold = ? WHERE id = ?",
        (new_status, item_id)
    )

    conn.commit()

    updated_item = conn.execute(
        "SELECT * FROM items WHERE id = ?",
        (item_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(updated_item))

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM items WHERE id = ?",
        (item_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "deleted"})

@app.route("/reports", methods=["POST"])
def add_report():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports (item_id, item_name, student, reason, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data.get("item_id"),
        data.get("item_name"),
        data.get("student"),
        data.get("reason"),
        "Pending"
    ))

    conn.commit()

    report_id = cursor.lastrowid

    new_report = conn.execute(
        "SELECT * FROM reports WHERE id = ?",
        (report_id,)
    ).fetchone()

    conn.close()

    return jsonify(dict(new_report))


@app.route("/reports", methods=["GET"])
def get_reports():
    conn = get_db_connection()
    reports = conn.execute("SELECT * FROM reports").fetchall()
    conn.close()

    return jsonify([dict(r) for r in reports])


@app.route("/reports/<int:report_id>", methods=["DELETE"])
def delete_report(report_id):
    conn = get_db_connection()

    conn.execute(
        "DELETE FROM reports WHERE id = ?",
        (report_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"message": "deleted"})


if __name__ == "__main__":
    app.run(debug=True)

