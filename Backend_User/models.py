from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 1. User Model: Handles Authentication & Seller Relationships
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False) 
    password = db.Column(db.String(200), nullable=False) # Supports pbkdf2:sha256 hashing
    role = db.Column(db.String(50), default="Student") 
    
    # Links a user to multiple marketplace listings
    items = db.relationship('Item', backref='seller', lazy=True)

# 2. Item Model: Strictly filtered for FCI Faculty resources
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    originalprice = db.Column(db.Float) # Used for Sustainability 'Savings' math
    faculty = db.Column(db.String(50), default="FCI") # Hardcoded for FCI Integrity
    department = db.Column(db.String(100)) # e.g., CS, SE, Game Dev
    
    # Supports the 2-category filter: 'Foundation', 'Diploma', or 'Degree'
    academic_level = db.Column(db.String(50)) 
    
    contact_info = db.Column(db.String(100))