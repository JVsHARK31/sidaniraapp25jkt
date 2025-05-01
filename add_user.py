import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from src.main import app, db # Import app and db from main
from src.models.user import User # Import User model

# Define the default user credentials
default_username = "Edwin"
default_password = "Edwin123"

def add_default_user():
    with app.app_context():
        # Check if the user already exists
        existing_user = User.query.filter_by(username=default_username).first()
        if existing_user:
            print(f"User 	{default_username}	 already exists.")
        else:
            # Create the new user
            new_user = User(username=default_username)
            new_user.set_password(default_password)
            db.session.add(new_user)
            db.session.commit()
            print(f"User 	{default_username}	 added successfully.")

if __name__ == "__main__":
    add_default_user()

