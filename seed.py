from app import app
from models import db, User, Item
from werkzeug.security import generate_password_hash

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Hash the password so login works!
        hashed_pw = generate_password_hash("securepassword123", method='pbkdf2:sha256')

        test_user = User(
            name="Azfar Hakim",
            email="azfar.hakim@mmu.edu.my",
            password=hashed_pw,
            role="Student"
        )
        db.session.add(test_user)
        db.session.commit()

        item1 = Item(
            title="Python for Data Science", 
            price=50.0, 
            originalprice=130.0, 
            faculty="FCI", 
            department="Data Science", 
            description="Useful for Year 2 FCI students",
            contact_info="012-3456789",
            seller_id=test_user.id
        )

        db.session.add(item1)
        db.session.commit()
        print("FCI Database seeded successfully!")

if __name__ == '__main__':
    seed_database()