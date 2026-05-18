from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """The permanent database table blueprint for registered FCI accounts"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False)
    level = db.Column(db.String(50), nullable=False) # 'Degree' or 'Diploma/Foundation'
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "student_id": self.student_id,
            "level": self.level,
            "email": self.email
        }

class Item(db.Model):
    """The permanent database table blueprint for marketplace listings"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    student = db.Column(db.String(100), nullable=False)   # Seller Name
    level = db.Column(db.String(50), nullable=False)       # Academic level tier focus
    sold = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.String(255), nullable=False, default="Pre-loved FCI course material.")
    buyer = db.Column(db.String(100), nullable=True)       # Tracks purchase history

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "student": self.student,
            "level": self.level,
            "sold": self.sold,
            "description": self.description,
            "buyer": self.buyer
        }