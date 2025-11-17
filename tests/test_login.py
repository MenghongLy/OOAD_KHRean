from main import create_app, db
from models.models import User
from werkzeug.security import generate_password_hash

app = create_app()

# Create test user
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="testuser").first():
        test_user = User(username="testuser", password=generate_password_hash(
            "testpass"), role="student")
        db.session.add(test_user)
        db.session.commit()

# Testing login route
with app.test_client() as client:
    # Correct login
    response = client.post(
        "/login", data={"username": "testuser", "password": "testpass"}, follow_redirects=True)
    print("Status code:", response.status_code)
    print("Response data:", response.data.decode())

    # Wrong login
    response = client.post(
        "/login", data={"username": "testuser", "password": "wrongpass"}, follow_redirects=True)
    print("Status code:", response.status_code)
    print("Response data:", response.data.decode())
