from app import app
from models import db, User, Item
from werkzeug.security import generate_password_hash

def seed_database():
    with app.app_context():
        # Clear existing data to prevent primary key conflicts
        db.drop_all()
        db.create_all()

        # 1. Create a Primary Test User (MMU Authenticated)
        hashed_pw = generate_password_hash("fcipassword2026", method='pbkdf2:sha256')
        admin_user = User(
            name="Azfar Hakim",
            email="azfar.hakim@student.mmu.edu.my",
            password=hashed_pw,
            role="Student"
        )
        db.session.add(admin_user)
        db.session.commit()

        # 2. Seed Items for Category 1: Foundation & Diploma (fd)
        item_fd_1 = Item(
            title="Digital Logic Design Kit", 
            price=80.0, 
            originalprice=150.0, 
            faculty="FCI", 
            academic_level="Foundation", # Logic handles this as 'fd'
            department="Computing", 
            description="Complete kit for Foundation in Computing students.",
            contact_info="012-3456789",
            seller_id=admin_user.id
        )
        
        item_fd_2 = Item(
            title="C++ Programming Guide", 
            price=30.0, 
            originalprice=75.0, 
            faculty="FCI", 
            academic_level="Diploma", # Also categorized as 'fd'
            department="Information Technology", 
            description="Essential for Diploma Year 1 programming modules.",
            contact_info="012-3456789",
            seller_id=admin_user.id
        )

        # 3. Seed Items for Category 2: Degree
        item_degree = Item(
            title="Artificial Intelligence Textbook", 
            price=120.0, 
            originalprice=250.0, 
            faculty="FCI", 
            academic_level="Degree", 
            department="Computer Science", 
            description="Reference book for AI and Machine Learning degree students.",
            contact_info="012-3456789",
            seller_id=admin_user.id
        )

        # Add all to session and commit
        db.session.add_all([item_fd_1, item_fd_2, item_degree])
        db.session.commit()
        
        print("FCI EcoLoop Database seeded successfully with 2-Category logic!")

if __name__ == '__main__':
    seed_database()