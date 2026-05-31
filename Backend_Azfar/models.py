from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    level = db.Column(db.String(50), nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user') 

    def to_dict(self):
        return {"id": self.id, "name": self.name, "student_id": self.student_id, "level": self.level, "email": self.email, "role": self.role}

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Float, nullable=False)
    student = db.Column(db.String(150), nullable=False)
    level = db.Column(db.String(50), nullable=True, default="Degree")
    description = db.Column(db.Text, nullable=True, default="Ecosystem trade asset listed across faculty nodes.")
    sold = db.Column(db.Boolean, default=False)
    buyer = db.Column(db.String(150), nullable=True)
    image = db.Column(db.Text, nullable=True)
    # ADDED FOR MAATHESH FRONTEND COMPATIBILITY
    faculty = db.Column(db.String(50), nullable=True, default="FCI") 

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)        
    statement = db.Column(db.Text, nullable=False)         
    image = db.Column(db.Text, nullable=True)              
    user_name = db.Column(db.String(100), nullable=False)