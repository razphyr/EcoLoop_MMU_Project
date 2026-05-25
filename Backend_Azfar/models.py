from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    level = db.Column(db.String(50), nullable=False) 
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user') # 'user' or 'admin'
    id = db.Column(db.Integer, primary_key=True)
    # ... your existing user fields (name, student_id, level, email, password, role) ...
    otp_secret = db.Column(db.String(32), nullable=True) # Stores the unique 32-character 2FA secret key

    def to_dict(self):
        return {"id": self.id, "name": self.name, "student_id": self.student_id, "level": self.level, "email": self.email, "role": self.role}

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    student = db.Column(db.String(100), nullable=False)   
    level = db.Column(db.String(50), nullable=False)       
    sold = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    buyer = db.Column(db.String(100), nullable=True)       

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)        # 'Report' or 'Feedback'
    statement = db.Column(db.Text, nullable=False)         
    image = db.Column(db.Text, nullable=True)              # Stores image as simple Base64 text string
    user_name = db.Column(db.String(100), nullable=False)