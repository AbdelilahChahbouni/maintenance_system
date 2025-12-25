from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # Check if admin exists by email or username
    if not User.query.filter((User.email == "admin@gmail.com") | (User.username == "admin")).first():
        user = User(
            username="admin",
            email="admin@gmail.com",
            first_name="Admin",
            last_name="User",
            role="admin",
            status="active",
            is_admin=True
        )
        user.set_password("admin123")
        db.session.add(user)
        db.session.commit()
        print("Admin user created successfully.")
    else:
        # Ensure existing admin is active
        user = User.query.filter((User.email == "admin@gmail.com") | (User.username == "admin")).first()
        if user and user.status != 'active':
            user.status = 'active'
            db.session.commit()
            print("Existing admin user unblocked.")
        else:
            print("Admin user already exists and is active.")
