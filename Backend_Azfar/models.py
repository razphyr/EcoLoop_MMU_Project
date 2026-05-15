from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(6), nullable=True)

# models.py - Add status and category
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    originalprice = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    faculty = db.Column(db.String(10), default="FCI")
    level = db.Column(db.String(20), default="Degree")
    category = db.Column(db.String(50), default="General") # e.g., 'Book', 'Electronics', 'Kit'
    status = db.Column(db.String(20), default="Available") # 'Available' or 'Sold'
    contact_info = db.Column(db.String(100))
    # Link item to a specific user
    owner_email = db.Column(db.String(120), db.ForeignKey('user.email'))