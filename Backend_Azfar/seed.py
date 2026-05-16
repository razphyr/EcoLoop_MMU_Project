from app import app, db
from models import Item, User
from werkzeug.security import generate_password_hash

# This block ensures the database operations have access to the app configuration
with app.app_context():
    try:
        print("Connecting to database...")
        # Deletes existing tables to ensure a clean start
        db.drop_all()
        # Creates the tables based on your updated models.py
        db.create_all()
        
        print("Adding sample MMU data...")
        
        # 1. Add a Verified Student Account
        # Using the correct MMU email domain as per project requirements
        test_user = User(
            name="Azfar Hakim", 
            email="azfar@student.mmu.edu.my", 
            password=generate_password_hash("mmu123", method='pbkdf2:sha256'),
            is_verified=True
        )
        db.session.add(test_user)
        
        # These will be used to calculate the smart CO2 offsets on the dashboard
        items = [
            Item(
                title="Digital Logic Design Kit", 
                price=45.0, 
                originalprice=90.0, 
                description="Complete breadboard and components for FCI Year 1.",
                faculty="FCI",
                level="Diploma_Foundation",
                category="Electronics",     
                status="Available",          
                contact_info="012-3456789",
                owner_email="test67@student.mmu.edu.my" 
            ),
            Item(
                title="Python Programming Textbook", 
                price=25.0, 
                originalprice=65.0, 
                description="Essential for CSP1114. Minimal highlights.",
                faculty="FCI",
                level="Diploma_Foundation",
                category="Book",             # <--- Drive advanced CO2 math
                status="Available",
                contact_info="013-9876543",
                owner_email="test456@student.mmu.edu.my"
            ),
            Item(
                title="Arduino Uno Rev3", 
                price=30.0, 
                originalprice=75.0, 
                description="Perfect for robotics projects. Includes USB cable.",
                faculty="FCI",
                level="Degree",
                category="Electronics",
                status="Available",
                contact_info="017-1122334",
                owner_email="test123@student.mmu.edu.my"
            ),
            Item(
                title="Advanced Data Structures Guide", 
                price=40.0, 
                originalprice=110.0, 
                description="Detailed notes for Year 2 Computer Science students.",
                faculty="FCI",
                level="Degree",
                category="Book",
                status="Available",
                contact_info="019-5566778",
                owner_email="test911@student.mmu.edu.my"
            )
        ]
        
        for item in items:
            db.session.add(item)
            
        db.session.commit()
        print("Database Successfully Initialized!")
        
    except Exception as e:
        print(f"An error occurred during seeding: {e}")
        db.session.rollback()