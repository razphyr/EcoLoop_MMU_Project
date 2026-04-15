from flask import Flask
from models import db  # This imports the logic you wrote in models.py

app = Flask(__name__)

# 1. Tell Flask where to create the database file
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecoloop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2. Connect the database to your app
db.init_app(app)

# 3. Create the database file and tables automatically
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "EcoLoop MMU: Database is Linked and Online!"

if __name__ == '__main__':
    app.run(debug=True)