from app import app, db
from models import Item, User
from werkzeug.security import generate_password_hash

with app.app_context():
    try:
        print("Connecting to database...")
        db.drop_all()
        db.create_all()
        
        print("Adding sample MMU data...")
        
        # 1. Add a Verified Student Account
        test_user = User(
            name="Azfar Hakim", 
            email="azfar@student.mmu.edu.my", 
            password=generate_password_hash("mmu123", method='pbkdf2:sha256'),
            is_verified=True
        )
        db.session.add(test_user)
        
        # 2. Add Sample FCI Marketplace Items with Academic Levels
        items = [
            Item(
                title="Digital Logic Design Kit", 
                price=45.0, 
                originalprice=90.0, 
                description="Complete breadboard and components for FCI Year 1.",
                faculty="FCI",
                level="Diploma_Foundation", #Matches the filter button
                contact_info="012-3456789"
            ),
            Item(
                title="Python Programming Textbook", 
                price=25.0, 
                originalprice=65.0, 
                description="Essential for CSP1114. Minimal highlights.",
                faculty="FCI",
                level="Diploma_Foundation", #Matches the filter button
                contact_info="013-9876543"
            ),
            Item(
                title="Arduino Uno Rev3", 
                price=30.0, 
                originalprice=75.0, 
                description="Perfect for robotics projects. Includes USB cable.",
                faculty="FCI",
                level="Degree", #Matches the Degree filter
                contact_info="017-1122334"
            ),
            Item(
                title="Advanced Data Structures Guide", 
                price=40.0, 
                originalprice=110.0, 
                description="Detailed notes for Year 2 Computer Science students.",
                faculty="FCI",
                level="Degree",
                contact_info="019-5566778"
            )
        ]
        
        for item in items:
            db.session.add(item)
            
        db.session.commit()
        print("Database Successfully Initialized and Seeded with academic levels!")
        
    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        db.session.rollback()