from TEst_Broke_Bite.app import app
from models import db, User

with app.app_context():
    # Fetch all user records directly from the database table matrix
    all_users = User.query.all()
    
    print("\n" + "="*60)
    print(f"👥 TOTAL REGISTERED USERS: {len(all_users)}")
    print("="*60)
    
    if not all_users:
        print("❌ No registration nodes discovered in the database yet.")
    
    for user in all_users:
        print(f"• Name:       {user.name}")
        print(f"  Student ID: {user.student_id}")
        print(f"  Level:      {user.level}")
        print(f"  Email:      {user.email}")
        print(f"  Password:   {user.password}") # Displays the password string clearly for testing
        print("-"*40)
    print("="*60 + "\n")