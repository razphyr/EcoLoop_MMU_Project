from app import app, db
from models import Item

with app.app_context():
    # Clear and recreate the database
    db.drop_all()
    db.create_all()
    
    # Add initial items for the marketplace
    db.session.add(Item(
        title="Digital Logic Design Kit", 
        price=45.0, 
        originalprice=90.0, 
        description="Complete set with breadboard. Used for one semester.",
        faculty="FCI"
    ))
    db.session.add(Item(
        title="Arduino Uno Rev3", 
        price=30.0, 
        originalprice=75.0, 
        description="Includes USB cable and sensors.",
        faculty="FCI"
    ))
    
    db.session.commit()
    print("Database Initialized!")