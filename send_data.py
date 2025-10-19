from app import create_app, db
from app.models import User
from faker import Faker
from datetime import datetime, timedelta
import random

app = create_app()
fake = Faker()

def add_users():
    with app.app_context():
        # Uncomment if you want to reset tables first (CAREFUL: deletes all data)
        # db.drop_all()
        # db.create_all()
        # db.create_all()
        users = []
        for _ in range(5):
            user = User(
                username=fake.user_name(),
                email=fake.email(),
                password_hash="hashedpassword",
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )
            db.session.add(user)
            users.append(user)

        db.session.commit()
        return f"{len(users)} users added successfully!"

if __name__ == "__main__":
    print(add_users())


