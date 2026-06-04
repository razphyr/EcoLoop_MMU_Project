from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    level = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), default="user")
    phone = db.Column(db.String(50), nullable=True)

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    student = db.Column(db.String(100), nullable=False)  # Seller Name Node
    faculty = db.Column(db.String(50), default="FCI")
    level = db.Column(db.String(50), default="Degree")
    description = db.Column(db.Text)
    image = db.Column(db.Text, nullable=True)             # Main item photo stream
    buyer = db.Column(db.String(100), nullable=True)
    fee_deducted = db.Column(db.Float, default=0.0)
    final_payout = db.Column(db.Float, default=0.0)
    
    # 🔄 STATUS STATE MACHINE PARAMETERS
    status = db.Column(db.String(20), default="available") # "available", "pending", "sold"
    delivery_proof = db.Column(db.Text, nullable=True)     # Base64 verification image string

class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    statement = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=True)
    user_name = db.Column(db.String(100), nullable=True)