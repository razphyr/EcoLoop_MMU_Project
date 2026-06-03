from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# Inside your models.py file, update your User class structure:
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    level = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')
    phone = db.Column(db.String(20), nullable=True)
    two_factor_linked = db.Column(db.Boolean, default=False)

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    student = db.Column(db.String(150), nullable=False)
    level = db.Column(db.String(50), nullable=True, default="Degree")
    description = db.Column(db.Text, nullable=True, default="Ecosystem trade asset listed across faculty platform.")
    sold = db.Column(db.Boolean, default=False)
    buyer = db.Column(db.String(150), nullable=True)
    image = db.Column(db.Text, nullable=True)
    faculty = db.Column(db.String(50), nullable=True, default="FCI") 

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)        
    statement = db.Column(db.Text, nullable=False)         
    image = db.Column(db.Text, nullable=True)              
    user_name = db.Column(db.String(100), nullable=False)