from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False) 
    password = db.Column(db.String(200), nullable=False) # Increased for security
    role = db.Column(db.String(50), default="Student") 
    items = db.relationship('Item', backref='seller', lazy=True)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    originalprice = db.Column(db.Float)
    faculty = db.Column(db.String(50), default="FCI")
    department = db.Column(db.String(100))
    contact_info = db.Column(db.String(100)) # Added for WhatsApp buttons