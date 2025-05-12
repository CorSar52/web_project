from app import app
from models import db, User, Article

with app.app_context():
    db.session.query(User).delete()
    db.session.query(Article).delete()
    db.session.commit()
    print("Database cleared.")
